from flask import Flask, render_template, request
import mysql.connector # type: ignore

app = Flask(__name__)
# app.config['TESTING'] = True

# database connection
db=mysql.connector.connect(
    host="localhost",   
    user="root",
    password="",
    database="sweet_shop"
)
cursor=db.cursor()

# define route 
@app.route('/')
def index():
    cursor.execute("SELECT * FROM sweets")
    sweets = cursor.fetchall()
    return render_template('HomePage.html', sweets=sweets)

# add the sweet to a database
@app.route('/add',methods=['POST'])
def add_sweet():
    id=request.form['id']
    s_name=request.form['sweet_name']
    s_category=request.form['category']
    s_price=request.form['price']
    s_qty=request.form['qty']
    
    sql="insert into sweets(id,s_name,s_category,s_price,s_qty) values(%s,%s,%s,%s,%s)"
    values=(id,s_name,s_category,s_price,s_qty)
    try:
        cursor.execute(sql, values)
        db.commit()
        return render_template('HomePage.html', message="✅ Sweet added successfully!")

    # give an error incase of data duplication
    except mysql.connector.IntegrityError as e:
        if "Duplicate entry" in str(e):
            return render_template('HomePage.html', message="❌ Sweet with this ID already exists!")
        else:
            return render_template('HomePage.html', message=f"❌ Error: {str(e)}")

# display sweets 
# @app.route('/sweets')
@app.route('/purchase')
def show_sweets():
    cursor.execute("select * from sweets")
    sweets= cursor.fetchall()
    return render_template('Purchase.html',sweets=sweets)

# restock the sweets and update it using id only
@app.route('/restock')
def sweet_restock():
    return render_template('Restock.html')

@app.route('/update_stock',methods=['POST'])
def update_stock():
    id=request.form['id']
    n_qty=int(request.form['qty'])
    s_price=request.form['price']
    
    sql="select s_qty from sweets where id=%s"
    cursor.execute(sql,(id,))
    result=cursor.fetchone()
    
    if result:
        s_qty=result[0]
        f_qty=s_qty+n_qty
        
        sql="update sweets set s_qty=%s,s_price=%s where id=%s"
        values=(f_qty,s_price,id)
        cursor.execute(sql,values)
        db.commit()
        return render_template('/Restock.html', message="Product restocked successfully!")
    else:
        return render_template('/Restock.html', message="Sweet Not Found")

#delete the stock by using id
@app.route('/delete_stock',methods=['POST'])
def delete_stock():
    id=request.form['id']
    sql="delete from sweets where id=%s"
    cursor.execute(sql,(id,))
    db.commit()
    return render_template('/Restock.html', message="Product Deleted successfully!")


@app.route('/purchase_sweet',methods=['POST'])
def purchase_swt():
    id=request.form['id']
    qty=int(request.form['qty'])
    sql="select s_qty from sweets where id=%s"
    cursor.execute(sql,(id,))
    result=cursor.fetchone()
    
    if result:
        s_qty=result[0]
        if s_qty >=qty:
            new_qty= s_qty-qty
            
            sql="update sweets set s_qty=%s where id=%s"
            cursor.execute(sql,(new_qty,id))
            db.commit()
            return render_template('/Purchase.html',message="Purchase Successfull")
        else:
            return render_template('/Purchase.html',message="Insufficient Stock")
    else:
        return render_template('/Purchase.html',message="Sweet Not Found")
            
            
    

if __name__=='__main__':
    app.run(debug=True)