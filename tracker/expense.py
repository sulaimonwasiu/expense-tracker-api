from flask import (
    Blueprint, current_app, jsonify, request
)
from flask_jwt_extended import get_jwt_identity, jwt_required
from datetime import datetime

from tracker.db import get_db

bp = Blueprint('expense', __name__)

@bp.route('/expenses', methods=['GET'])
@jwt_required()
def get_expenses():
    current_user = get_jwt_identity()  # Get the current user's identity (username or user ID)

    with get_db() as db:
        expenses = db.execute(
            'SELECT * FROM expense WHERE user_id=?', (current_user,)
        ).fetchall()

    # Convert the fetched expenses to a list of dictionaries
    expenses_list = [dict(expense) for expense in expenses]

    # Return the list of expenses
    return jsonify(expenses_list), 200


@bp.route('/expenses/<int:expense_id>', methods=['GET'])
@jwt_required()
def get_expense(expense_id):
    current_user = get_jwt_identity()  # Get the current user's identity (username or user ID)

    with get_db() as db:
        # Fetch the expense record for the current user
        expense = db.execute(
            'SELECT * FROM expense WHERE id = ? AND user_id = ?', (expense_id, current_user)
        ).fetchone()

    if expense is None:
        return jsonify({'msg': 'Expense not found or not authorized.'}), 404

    # Convert the fetched expense to a dictionary
    expense_dict = dict(expense)

    return jsonify(expense_dict), 200


@bp.route('/expenses', methods=['POST'])
@jwt_required()
def add_expense():
    current_user = get_jwt_identity()  # Get the current user's identity (username or user ID)

    # Get data from the request
    data = request.get_json()
    description = data.get('description')
    amount = data.get('amount')
    
    # Generate current date and time
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Format the date

    # Validate input
    if not description or amount is None:
        return jsonify({'msg': 'Description and amount are required.'}), 400

    # Assuming current_user is the user's ID; adjust if needed based on your JWT setup
    user_id = current_user  # This may be the username or user ID depending on your JWT payload

    # Insert the expense into the database
    try:
        with get_db() as db:
            db.execute(
                'INSERT INTO expense (description, amount, date, user_id) VALUES (?, ?, ?, ?)',
                (description, amount, date, user_id)
            )
            db.commit()
        return jsonify({'msg': 'Expense added successfully.'}), 201
    except Exception as e:
        return jsonify({'msg': 'Error adding expense.', 'error': str(e)}), 500
    

@bp.route('/expenses/<int:expense_id>', methods=['DELETE'])
@jwt_required()
def delete_expense(expense_id):
    current_user = get_jwt_identity()

    with get_db() as db:
        expense = db.execute(
            'SELECT * FROM expense WHERE id = ? AND user_id = ?', (expense_id, current_user)
        ).fetchone()
        
        if expense is None:
            return jsonify({'msg': 'Expense not found or not authorized.'}), 404

        db.execute('DELETE FROM expense WHERE id = ?', (expense_id,))
        db.commit()

    return jsonify({'msg': 'Expense deleted successfully.'}), 200


@bp.route('/expenses/<int:expense_id>', methods=['PUT'])
@jwt_required()
def update_expense(expense_id):
    current_user = get_jwt_identity()

    data = request.get_json()
    description = data.get('description')
    amount = data.get('amount')
    
    if description is None and amount is None:
        return jsonify({'msg': 'Description or amount must be provided.'}), 400

    fields_to_update = []
    values = []

    if description is not None:
        fields_to_update.append('description = ?')
        values.append(description)

    if amount is not None:
        fields_to_update.append('amount = ?')
        values.append(amount)

    values.append(expense_id)

    with get_db() as db:
        expense = db.execute(
            'SELECT * FROM expense WHERE id = ? AND user_id = ?', (expense_id, current_user)
        ).fetchone()
        
        if expense is None:
            return jsonify({'msg': 'Expense not found or not authorized.'}), 404

        db.execute(
            f'UPDATE expense SET {", ".join(fields_to_update)} WHERE id = ?',
            values
        )
        db.commit()

    return jsonify({'msg': 'Expense updated successfully.'}), 200