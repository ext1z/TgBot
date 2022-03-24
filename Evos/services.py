import sqlite3

con = sqlite3.connect("Evos.db", check_same_thread=False)
cur = con.cursor()


def get_log(user_id):
    sql = f'select * from log where user_id={user_id}'
    cur.execute(sql)
    return cur.fetchone()


def create_log(user_id):
    a = {'state': 0}
    sql = f"""insert into log values ({user_id}, "{a}") """
    print(sql)
    cur.execute(sql)
    con.commit()
    return get_log(user_id)


def change_log(user_id, log):
    sql = f'''update log set messages="{log}" where user_id={user_id}'''
    cur.execute(sql)
    con.commit()


def get_user(user_id):
    sql = f'select * from user where user_id={user_id}'
    cur.execute(sql)
    return cur.fetchone()


def add_user(user_id, log):
    ism = log.get('ism', '')
    familiya = log.get('familiya', '')
    raqam = log.get('raqam', '')
    sql = f"insert into user values({user_id}, '{ism}', '{familiya}', '{raqam}')"
    cur.execute(sql)
    con.commit()


def clear_log(user_id, state):
    log = {'state': state}
    sql = f'''update log set messages="{log}" where user_id={user_id}'''
    cur.execute(sql)
    con.commit()


def get_ctgs():
    sql = 'select * from category'
    cur.execute(sql)
    return cur.fetchall()


def get_products(name=None, ctg=None, ):
    if name:
        sql = f"""
        select * from product
        where name="{name}"
        """
        return cur.execute(sql).fetchone()

    elif ctg:
        sql = f"""
        select product.id, product.name, product.tarkib, product.price, ctg.nomi, ctg.slug from product
        inner join category ctg on ctg.id = product.ctg
        where ctg.nomi = '{ctg}'
        """
        return cur.execute(sql).fetchall()


def get_ctg(ctg):
    sql = f"""
    select * from category
    where nomi = '{ctg}'
    """
    return cur.execute(sql).fetchone()





