import sqlite3
import csv
import time
import numpy as np
import pandas as pd
import tensorflow as tf
from flask import Flask, jsonify, request, g
from datetime import datetime
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app, template_file='swagger_template.yaml')
DATABASE = 'movidation.db'

model_path = 'autoencoder_model_256.h5'
autoencoder = tf.keras.models.load_model(model_path)
 


# Function to get top 50 movies for a specific user
def recommend_for_user(user_id):
    ratings = pd.read_csv('ratings.csv')  # Adjust path to ratings.csv
    ratings.columns = ['UserID', 'MovieID', 'Rating', 'Timestamp']

    movies = pd.read_csv('movies.csv', encoding='ISO-8859-1')
    movies.columns = ['MovieID', 'Title', 'Genres']
    # Create the user-movie ratings pivot table
    ratings_pivot = pd.pivot_table(ratings[['UserID', 'MovieID', 'Rating']],
                                values='Rating', index='UserID', columns='MovieID').fillna(0)

    # Map movie IDs to their indices
    movie_id_to_index = {movie_id: index for index, movie_id in enumerate(ratings_pivot.columns)}
    index_to_movie_id = {index: movie_id for movie_id, index in movie_id_to_index.items()}
    if user_id not in ratings_pivot.index:
        return None  # User not found
    # Extract the user's rating vector
    user_ratings = ratings_pivot.loc[user_id].values.reshape(1, -1)
    # Predict ratings
    predicted_ratings = autoencoder.predict(user_ratings).flatten()
    # Exclude already rated movies
    already_rated = user_ratings.flatten() > 0
    recommendation_scores = np.where(already_rated, -np.inf, predicted_ratings)
    # Get the top 50 movie indices
    top_indices = np.argsort(recommendation_scores)[::-1][:50]
    # Map indices to MovieID
    top_movie_ids = [index_to_movie_id[i] for i in top_indices]
    return top_movie_ids

# Function to get top 50 movies globally (most popular)
def recommend_globally():
    ratings = pd.read_csv('ratings.csv')  # Adjust path to ratings.csv
    # Calculate average rating for each movie
    global_avg_ratings = ratings.groupby('MovieID')['Rating'].mean()
    # Sort by average rating and get the top 50 MovieIDs
    top_global_movie_ids = global_avg_ratings.sort_values(ascending=False).head(50).index.tolist()
    return top_global_movie_ids

# Fungsi untuk koneksi database
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# Tutup koneksi database saat aplikasi selesai
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Endpoint registrasi
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')


    if not username or not password:
        return jsonify({"error": "Username password are required"}), 400

    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (?,?)', (username,password))
        db.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exists"}), 400

# Endpoint login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    db = get_db() 
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
 
    if user:
        id = user[0]
        return jsonify({"message": "Login successful", "user_id" : id}), 200
    return jsonify({"error": "Invalid username or password"}), 401

@app.route('/getuser', methods=['GET'])
def get_user():
    try:
        # Ambil parameter user_id dari query
        user_id = request.args.get('user_id')

        # Validasi input
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400

        # Query database untuk mendapatkan data user
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT id, username FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()

        if user:
            # User ditemukan, kembalikan data user
            user_data = {
                "id": user[0],
                "username": user[1]
            }
            return jsonify({"message": "User found", "user": user_data}), 200
        else:
            # User tidak ditemukan
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        print(f"Error: {e}")  # Log error
        return jsonify({"error": "Something went wrong"}), 500

@app.route('/topmovie', methods=['GET'])
def get_topMovie():
    try:
    
        # Query database untuk mendapatkan data user
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''SELECT * FROM detail_movie
                       ORDER BY rating DESC,release_date DESC
                       LIMIT 50
                       ''')
        results = cursor.fetchall()
        if results:
            list_movie = []
            for data in results:
                movie = {
                    'movie_id' : data[0],
                    'movie_name' : data[2],
                    'poster_path': data[4]
                }
                list_movie.append(movie)

            return jsonify({"result":list_movie})
        else:
            return jsonify({"error": "Movie Not Found"}), 404
    except Exception as e:
        print(f"Error: {e}")  # Log error
        return jsonify({"error": "Something went wrong"}), 500

@app.route('/randmovie', methods=['GET'])
def get_randMovie():
    try:
    
        # Query database untuk mendapatkan data user
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''SELECT * FROM detail_movie
                       ORDER BY RANDOM()
                       LIMIT 50
                       ''')
        results = cursor.fetchall()
        if results:
            list_movie = []
            for data in results:
                movie = {
                    'movie_id' : data[0],
                    'movie_name' : data[2],
                    'poster_path': data[4]
                }
                list_movie.append(movie)

            return jsonify({"result":list_movie})
        else:
            return jsonify({"error": "Movie Not Found"}), 404
    except Exception as e:
        print(f"Error: {e}")  # Log error
        return jsonify({"error": "Something went wrong"}), 500
    
@app.route('/getmovie', methods=['GET'])
def get_movie():
    try:
        movie_id = request.args.get('movie_id')
            
        if not movie_id:
            return jsonify({"error": "movie_id is required"}), 400
        # Query database untuk mendapatkan data user
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''SELECT * FROM detail_movie
                       WHERE movie_id = ?
                       ''',(movie_id,))
        results = cursor.fetchone()
        if results:
            movie = {
            'movie_id': results[0],
            'tmdb_id': results[1],
            'movie_name': results[2],
            'rating': results[3],
            'poster_link': results[4],
            'release_date': results[5],
            'desc': results[6]
            }

            return jsonify({"result":movie})
        else:
            return jsonify({"error": "Movie Not Found"}), 404
    except Exception as e:
        print(f"Error: {e}")  # Log error
        return jsonify({"error": "Something went wrong"}), 500

@app.route('/giverating', methods=['POST'])
def giveRating():
    file_rating = 'ratings.csv'

    data = request.get_json()
    user_id = data.get('user_id')
    movie_id = data.get('movie_id')
    rating = data.get('rating')
    comment = data.get('comment')
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    timestamp = int(time.time())

    if not user_id or not movie_id or not rating or not comment:
        return jsonify({"error": "Missing Parameter"}), 400
    try: 
        new_row = {'userId': user_id, 'movieId': movie_id, 'rating': float(rating), 'timestamp': timestamp}

        # Menambahkan baris baru
        with open(file_rating, mode='a', newline='', encoding='utf-8') as file:
            # Membuat writer dengan header
            writer = csv.DictWriter(file, fieldnames=new_row.keys())
            
            # Tambahkan baris data baru
            writer.writerow(new_row)

        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
                INSERT INTO ratings (user_id, movie_id, rating, comment, timestamp)
                VALUES (?, ?, ?, ?,?)
            ''', (user_id, movie_id, rating, comment, current_time))
        db.commit()

        return jsonify({"message": "Rating created successfully!"}), 201
    except sqlite3.IntegrityError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        db = get_db()
        cursor = db.cursor()
        # Get input data
        data = request.json
        user_id = data.get('user_id')
        print(user_id)

        # Check if user_id is valid
        if user_id is None or not isinstance(user_id, int):
            return jsonify({"error": "Invalid user_id"}), 400

        # Generate recommendations
        top_movie_ids = recommend_for_user(user_id)
        if top_movie_ids is None:  # If user ID is not in the dataset
            top_movie_ids = recommend_globally()

        list_movie = []
        for id in top_movie_ids:
            cursor.execute('''SELECT * FROM detail_movie
                        WHERE movie_id = ?
                        ''',(id,))
            data = cursor.fetchone()
            movie = {
                    'movie_id' : data[0],
                    'movie_name' : data[2],
                    'poster_path': data[4]
                }
            list_movie.append(movie)
        # Return recommendations as JSON
        return jsonify({"result": list_movie}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True)
