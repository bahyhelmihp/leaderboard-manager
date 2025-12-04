import os
from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize Firebase Admin SDK
cred_path = 'ssot-aibrain-46e556103f6f.json'
if not os.path.exists(cred_path):
    raise FileNotFoundError(f"Credentials file not found at {cred_path}")

cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)

db = firestore.client()

@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    drill_name = request.args.get('drill_name')
    
    if not drill_name:
        return jsonify({'error': 'drill_name parameter is required'}), 400

    valid_drills = [
        'reactionHandSessions',
        'reactionFootSessions',
        'dribbleSessions',
        'jugglingSessions',
        'getInTheBoxSessions',
        'theRainSessions',
        'followThePathBallSessions',
        'followThePathBodySessions'
    ]

    if drill_name not in valid_drills:
        return jsonify({'error': 'Invalid drill_name', 'valid_drills': valid_drills}), 400

    try:
        leaderboard = []
        users_ref = db.collection('users')
        users = users_ref.stream()

        for user in users:
            user_id = user.id
            user_data = user.to_dict()
            # Get display name by concatenating firstName and lastName
            first_name = user_data.get('firstName', '')
            last_name = user_data.get('lastName', '')
            user_name = f"{first_name} {last_name}".strip() or user_id

            drill_sessions_ref = users_ref.document(user_id).collection(drill_name)
            sessions = drill_sessions_ref.stream()

            total_score = 0
            for session in sessions:
                session_data = session.to_dict()
                score = session_data.get('score', 0)
                # Ensure score is a number
                if isinstance(score, (int, float)):
                    total_score += score

            if total_score > 0:
                leaderboard.append({
                    'user_id': user_id,
                    'name': user_name,
                    'total_score': total_score
                })

        # Sort by total_score in descending order
        leaderboard.sort(key=lambda x: x['total_score'], reverse=True)

        return jsonify(leaderboard), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run()
