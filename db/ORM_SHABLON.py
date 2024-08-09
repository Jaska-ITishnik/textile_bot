import psycopg2


class DB:
    con = psycopg2.connect(
        database="txtil_db",
        user="postgres",
        password="100",
        host="localhost",
        port=5432
    )
    cursor = con.cursor()

    def insert(self):
        table_name = self.__class__.__name__.lower() + "s"
        column_name = self.__dict__.keys()
        params = tuple(self.__dict__.values())
        column_name = ",".join(list(column_name))
        format = len(column_name.split(",")) * "%s, "
        query = f"""
        insert into {table_name} ({column_name})
        values ({format.strip(", ")})
        """
        self.cursor.execute(query, params)
        self.con.commit()

    def update(self, **kwargs):
        # User(name="New_value").update(which_user_exactly_update)
        table_name = self.__class__.__name__.lower() + "s"
        column_names_con = " = %s and ".join(kwargs.keys()) + " = %s"
        params_condition = tuple(kwargs.values())
        params_new = list(map(list, list(self.__dict__.items())))
        for p in range(len(params_new)):
            if not params_new[p][1].isdigit():
                params_new[p][1] = "\"" + params_new[p][1] + "\""

        for i in range(len(params_new)):
            params_new[i] = " = ".join(params_new[i])
        params_new = ", ".join(params_new)
        not_none_cols = []
        for item in list(self.__dict__.items()):
            if item[1]:
                not_none_cols.append(str(item[0]))
        if not_none_cols:
            query = f"""
                update {table_name} set {params_new} where {column_names_con};
            """
        else:
            query = f"""
                update {table_name} set {params_new};
            """
        # self.cursor.execute(query, params_condition)
        # self.con.commit()
        return query

    def delete(self, **conditions):
        table_name = self.__class__.__name__.lower() + "s"
        column_names = f" = %s and ".join(self.__dict__.keys()) + " = %s"
        params = tuple(conditions.values())
        query = f"""
            delete from {table_name} where {column_names};
        """
        self.cursor.execute(query, params)
        self.con.commit()

    def select(self, *param, **cond):
        table_name = self.__class__.__name__.lower() + 's'
        cond_maket = "where " + " = %s and ".join(list(cond.keys())) + " = %s" if cond else ""
        cond_values = tuple(cond.values())
        columns = '*' if not param else ", ".join(param)
        query = f"""
            select {columns} from {table_name} {cond_maket} order by id;
        """
        self.cursor.execute(query, cond_values)
        result = self.cursor.fetchall()
        return result

    def delete_task(self, pk: int):
        query = f"""
            delete from tasks where id = %s; 
        """
        self.cursor.execute(query, (pk,))
        self.con.commit()

    def update_task_employee(self, **kwargs):
        table_name = self.__class__.__name__.lower() + 's'
        params = " = %s, ".join(list(kwargs.keys())[:-1]) + ' = %s'
        condition = list(kwargs.keys())[-1] + ' = %s'
        values = tuple(kwargs.values())
        query = f"""
        update {table_name} set {params} where {condition};
        """
        self.cursor.execute(query, values)
        self.con.commit()

    def delete_employee(self, id):
        query = f"""
                    delete from employees where id = %s; 
                """
        self.cursor.execute(query, (id,))
        self.con.commit()

    def delete_user(self, telegram_id):
        query = f"""
                    delete from users where telegram_id = %s; 
                """
        self.cursor.execute(query, (telegram_id,))
        self.con.commit()
