from flask import Flask, jsonify, request

app = Flask(__name__)

students = [
    {"id": 1, "name": "Иванов Иван", "group": "ИТ-21", "age": 19},
    {"id": 2, "name": "Петрова Анна", "group": "ИТ-21", "age": 18},
    {"id": 3, "name": "Сидоров Пётр", "group": "ЭК-20", "age": 20}
]

@app.route('/students', methods=['GET'])
def get_students():
    return jsonify(students)

@app.route('/students/<int:id>', methods=['GET'])
def get_student(id):
    student = next((s for s in students if s["id"] == id), None)
    return jsonify(student) if student else (jsonify({"error": "Студент не найден"}), 404)

@app.route('/students', methods=['POST'])
def create_student():
    if not request.json or 'name' not in request.json:
        return jsonify({"error": "Поле name обязательно"}), 400
    
    new_student = {
        "id": max(s["id"] for s in students) + 1 if students else 1,
        "name": request.json["name"],
        "group": request.json.get("group", "Не указана"),
        "age": request.json.get("age", 18)
    }
    students.append(new_student)
    return jsonify(new_student), 201

@app.route('/students/<int:id>', methods=['PUT'])
def update_student(id):
    student = next((s for s in students if s["id"] == id), None)
    if not student:
        return jsonify({"error": "Студент не найден"}), 404
    if not request.json:
        return jsonify({"error": "Требуется JSON"}), 400
    
    student["name"] = request.json.get("name", student["name"])
    student["group"] = request.json.get("group", student["group"])
    student["age"] = request.json.get("age", student["age"])
    
    return jsonify(student)

@app.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    global students
    old_len = len(students)
    students = [s for s in students if s["id"] != id]
    if len(students) == old_len:
        return jsonify({"error": "Студент не найден"}), 404
    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)