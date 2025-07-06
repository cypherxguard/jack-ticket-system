from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from functools import wraps
from .models import db, User
from .forms import LoginForm, UserForm, ChangePasswordForm
from .utils import hash_password, verify_password

auth = Blueprint('auth', __name__)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            flash('Admin access required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and verify_password(user.password_hash, form.password.data):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))

@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = User.query.get(session['user_id'])
        if verify_password(user.password_hash, form.old_password.data):
            user.password_hash = hash_password(form.new_password.data)
            db.session.commit()
            flash('Password changed successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Current password is incorrect.', 'error')
    
    return render_template('auth/change_password.html', form=form)

@auth.route('/manage_users')
@admin_required
def manage_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('auth/manage_users.html', users=users)

@auth.route('/add_user', methods=['GET', 'POST'])
@admin_required
def add_user():
    form = UserForm()
    if form.validate_on_submit():
        # Check if username already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists.', 'error')
        elif not form.password.data:
            flash('Password is required for new users.', 'error')
        else:
            user = User(
                username=form.username.data,
                password_hash=hash_password(form.password.data),
                role=form.role.data
            )
            db.session.add(user)
            db.session.commit()
            flash('User created successfully!', 'success')
            return redirect(url_for('auth.manage_users'))
    
    return render_template('auth/add_user.html', form=form)

@auth.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    
    if form.validate_on_submit():
        # Check if username already exists (excluding current user)
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user and existing_user.id != user.id:
            flash('Username already exists.', 'error')
        else:
            user.username = form.username.data
            user.role = form.role.data
            if form.password.data:  # Only update password if provided
                user.password_hash = hash_password(form.password.data)
            db.session.commit()
            flash('User updated successfully!', 'success')
            return redirect(url_for('auth.manage_users'))
    
    return render_template('auth/edit_user.html', form=form, user=user)

@auth.route('/delete_user/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevent admin from deleting themselves
    if user.id == session['user_id']:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('auth.manage_users'))
    
    # Prevent deleting the last admin
    if user.role == 'admin':
        admin_count = User.query.filter_by(role='admin').count()
        if admin_count <= 1:
            flash('Cannot delete the last admin user.', 'error')
            return redirect(url_for('auth.manage_users'))
    
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('auth.manage_users'))

@auth.route('/reset_password/<int:user_id>', methods=['POST'])
@admin_required
def reset_password(user_id):
    user = User.query.get_or_404(user_id)
    new_password = request.form.get('new_password')
    
    if not new_password or len(new_password) < 6:
        flash('Password must be at least 6 characters long.', 'error')
    else:
        user.password_hash = hash_password(new_password)
        db.session.commit()
        flash(f'Password for {user.username} has been reset.', 'success')
    
    return redirect(url_for('auth.manage_users')) 