from flask.templating import render_template_string
from werkzeug.datastructures import RequestCacheControl

from application import app
from flask import Blueprint, render_template, request, redirect, flash, url_for
from .forms import BookForm
from application import db
from datetime import datetime
from functools import wraps

from bson import ObjectId
from bson.json_util import dumps

from application.bookfocusing.routes import login_required, manager_required

import time
from threading import Timer

login_required(wraps)
manager_required(wraps)


search = Blueprint(
    "search",
    __name__,
    template_folder="templates",
    static_folder="static"
)


# book db
@search.route("/management")
@login_required
@manager_required
def management():
    page = request.args.get("page", 1, type=int)
    name = request.args.get("name")
    per_page = 2  # Number of items per page

    # Construct the query based on the search name if provided
    query = {}
    if name:
        query["title"] = {"$regex": name, "$options": "i"}  # Search by title

    total_books = db.book_info.count_documents(query)  # Get the total number of books
    total_pages = (total_books + per_page - 1) // per_page  # Calculate the total number of pages

    cursor = db.book_info.find(query).sort("date_created", -1).skip((page - 1) * per_page).limit(per_page)
    todos = []
    for todo in cursor:
        todo["_id"] = str(todo["_id"])
        todo["date_created"] = todo["date_created"].strftime("%b %d %Y %H:%M%S")
        todos.append(todo)

    return render_template("search/manage.html", todos=todos, current_page=page, total_pages=total_pages, search_name=name)


# 책 추가입력 creat
@search.route("/add_book", methods=["POST", "GET"])
@login_required
@manager_required
def add_book():
    if request.method == "POST":                # 입력받기
        form = BookForm(request.form)
        book_title = form.title.data
        book_shelf = form.shelf.data
        book_block = form.block.data
        book_writer = form.writer.data
        book_loan = form.loan.data

        db.book_info.insert_one({               # MongoDB에 insert
            "title": book_title,
            "shelf": book_shelf,
            "block": book_block,
            "writer": book_writer,
            "loan": book_loan,
            "flag": '0',
            "date_created": datetime.utcnow()
        })
        flash("Todo successfully added", "success")         # 성공했다는 flask창
        return redirect(url_for("search.management"))
    else:
        form = BookForm()
    return render_template("search/crud_book.html", form=form)


# book db update
@search.route("/update_book/<id>", methods=['POST', 'GET'])
@login_required
@manager_required
def update_book(id):
    if request.method == "POST":
        form = BookForm(request.form)
        book_title = form.title.data
        book_shelf = form.shelf.data
        book_block = form.block.data
        book_writer = form.writer.data
        book_loan = form.loan.data

        db.book_info.find_one_and_update({"_id": ObjectId(id)}, {"$set": {
            "title": book_title,
            "shelf": book_shelf,
            "block": book_block,
            "writer": book_writer,
            "loan": book_loan,
            "flag": '0',
            "date_created": datetime.utcnow()
        }})
        flash("Todo successfully updated", "success")
        return redirect(url_for("search.management"))
    else:
        form = BookForm()

        search = db.book_info.find_one_or_404({"_id": ObjectId(id)})
        form.title.data = search.get("title", None)
        form.shelf.data = search.get("shelf", None)
        form.block.data = search.get("block", None)
        form.writer.data = search.get("writer", None)
        form.loan.data = search.get("loan", None)
    return render_template("search/crud_book.html", form=form)


# book db delete
@login_required
@manager_required
@search.route("/delete_book/<id>")
@login_required
def delete_book(id):
    db.book_info.find_one_and_delete({"_id": ObjectId(id)})
    return redirect(url_for("search.management"))

#도서 검색
@search.route("/books", methods=["POST", "GET"])
def books():
    if request.method == 'POST':
        form = BookForm(request.form)
        needbook = form.title.data
        # db.book_info.find_one({"title": txt})
        return redirect(url_for("search.book", needbook=needbook))
    else:
        form = BookForm()
    return render_template("search/books.html", form=form)


@search.route("/book/<needbook>")
def book(needbook):
    page = request.args.get("page", 1, type=int)
    per_page = 3  # Number of items per page

    # Calculate the skip value based on the current page
    skip = (page - 1) * per_page

    needs = []
    total_needs = db.book_info.count_documents({"title": needbook})
    total_pages = (total_needs + per_page - 1) // per_page

    for need in db.book_info.find({"title": needbook}).skip(skip).limit(per_page):
        need["_id"] = str(need["_id"])
        needs.append(need)

    return render_template("search/list.html", needs=needs, total_pages=total_pages)


@search.route("/flag/<id>")
def flag(id):
    db.book_info.find_one_and_update({"_id": ObjectId(id)}, {"$set": {"flag": '1'}})
    flash("블럭이 곧 작동됩니다. 해당하는 책장으로 이동해주십시오.")
    return redirect(url_for("search.books"))
