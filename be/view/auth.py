from flask import Blueprint
from flask import request
from flask import jsonify
from be.model import user

bp_auth = Blueprint("auth", __name__, url_prefix="/auth")


@bp_auth.route("/login", methods=["POST"])
def login():
    user_id = request.json.get("user_id", "")
    password = request.json.get("password", "")
    terminal = request.json.get("terminal", "")
    u = user.User()
    code, message, token = u.login(
        user_id=user_id, password=password, terminal=terminal
    )
    return jsonify({"message": message, "token": token}), code


@bp_auth.route("/logout", methods=["POST"])
def logout():
    user_id: str = request.json.get("user_id")
    token: str = request.headers.get("token")
    u = user.User()
    code, message = u.logout(user_id=user_id, token=token)
    return jsonify({"message": message}), code


@bp_auth.route("/register", methods=["POST"])
def register():
    user_id = request.json.get("user_id", "")
    password = request.json.get("password", "")
    u = user.User()
    code, message = u.register(user_id=user_id, password=password)
    return jsonify({"message": message}), code


@bp_auth.route("/unregister", methods=["POST"])
def unregister():
    user_id = request.json.get("user_id", "")
    password = request.json.get("password", "")
    u = user.User()
    code, message = u.unregister(user_id=user_id, password=password)
    return jsonify({"message": message}), code


@bp_auth.route("/password", methods=["POST"])
def change_password():
    user_id = request.json.get("user_id", "")
    old_password = request.json.get("oldPassword", "")
    new_password = request.json.get("newPassword", "")
    u = user.User()
    code, message = u.change_password(
        user_id=user_id, old_password=old_password, new_password=new_password
    )
    return jsonify({"message": message}), code

@bp_auth.route("/search_book", methods=["GET"])
def search_book():
    query_text = request.json.get("query_text", "")   # 获取查询文本
    page = request.json.get("page", 1)                # 获取当前页码，默认值为1
    page_size = request.json.get("page_size", 10)     # 获取每页的书籍数量，默认值为10
    store_id = request.json.get("store_id")           # 获取 store_id 参数，如果存在

    u = user.User()
    code, message, book_list = u.search_book(query_text, page, page_size, store_id)
    
    return jsonify({"message": message, "book_list": book_list}), code

@bp_auth.route("/search_book_regex", methods=["GET"])
def search_book_regex():
    query_text = request.json.get("query_text", "")   # 获取查询文本
    page = request.json.get("page", 1)                # 获取当前页码，默认值为1
    page_size = request.json.get("page_size", 10)     # 获取每页的书籍数量，默认值为10
    store_id = request.json.get("store_id")           # 获取 store_id 参数，如果存在

    u = user.User()
    code, message, book_list = u.search_book_regex(query_text, page, page_size, store_id)
    
    return jsonify({"message": message, "book_list": book_list}), code


@bp_auth.route("/recommend_books", methods=["GET"])
def recommend_books():
    buyer_id = request.args.get("buyer_id", "").strip()
    n_recommendations = request.args.get("n_recommendations", 5)  # 默认推荐5本书
    if not buyer_id:
        return jsonify({"message": "User ID is required."}), 400
    try:
        n_recommendations = int(n_recommendations)
    except ValueError:
        return jsonify({"message": "Invalid number of recommendations."}), 400
    
    u = user.User()
    code, books = u.recommend_books(buyer_id=buyer_id, n_recommendations=n_recommendations)

    if code == 200:
        return jsonify({"message": "Recommendations fetched successfully", "books": books}), 200
    else:
        return jsonify({"message": "Failed to fetch recommendations"}), code