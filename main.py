import pandas as pd

# Загрузка данных из JSON-файла
data = pd.read_json('data.json')

# Вычисление тарифа стоимости доставки для каждого склада
warehouse_tariffs = data.groupby("warehouse_name")["highway_cost"].sum()

# Вычисление общего количества, дохода, расхода и прибыли для каждого продукта
product_data = []
for _, row in data.iterrows():  # Итерация по каждой строке в DataFrame
    for product_info in row["products"]:  # Итерация по списку продуктов в поле "products"
        product_data.append(
            {
                "product": product_info["product"],
                "quantity": product_info["quantity"],
                "income": product_info["price"] * product_info["quantity"],
                "expenses": warehouse_tariffs[row["warehouse_name"]] * product_info["quantity"],
            }
        )
product_df = pd.DataFrame(product_data)

# Вычисление прибыли для каждого продукта
product_df["profit"] = product_df["income"] - product_df["expenses"]

# Вычисление прибыли для каждого заказа
order_data = []
for _, row in data.iterrows():  # Итерация по каждой строке в DataFrame
    order_profit = sum(
        product_info["price"] * product_info["quantity"]
        - warehouse_tariffs[row["warehouse_name"]] * product_info["quantity"]
        for product_info in row["products"]
    )
    order_data.append({"order_id": row["order_id"], "order_profit": order_profit})

# Создание DataFrame для данных о заказах и прибыли
order_df = pd.DataFrame(order_data)

# Вычисление средней прибыли
average_profit = order_df["order_profit"].mean()

# Вычисление процентной прибыли для каждого продукта относительно прибыли склада
warehouse_product_data = []
for _, row in data.iterrows():  # Итерация по каждой строке в DataFrame
    warehouse_total_profit = sum(
        product_info["price"] * product_info["quantity"]
        - warehouse_tariffs[row["warehouse_name"]] * product_info["quantity"]
        for product_info in row["products"]
    )
    for product_info in row["products"]:  # Итерация по списку продуктов в поле "products"
        product_profit = product_info["price"] * product_info["quantity"] - warehouse_tariffs[row["warehouse_name"]] * product_info["quantity"]
        percent_profit = (product_profit / warehouse_total_profit) * 100
        warehouse_product_data.append(
            {
                "warehouse_name": row["warehouse_name"],
                "product": product_info["product"],
                "quantity": product_info["quantity"],
                "profit": product_profit,
                "percent_profit_product_of_warehouse": percent_profit,
            }
        )

# Создание DataFrame для данных о продуктах и складах
warehouse_product_df = pd.DataFrame(warehouse_product_data)

# Сортировка DataFrame по процентной прибыли продуктов склада в порядке убывания
warehouse_product_df = warehouse_product_df.sort_values(
    by="percent_profit_product_of_warehouse", ascending=False
)

# Вычисление накопленного процента прибыли
warehouse_product_df["accumulated_percent_profit_product_of_warehouse"] = warehouse_product_df[
    "percent_profit_product_of_warehouse"
].cumsum()

# Функция для присвоения категории на основе накопленного процента прибыли
def assign_category(accumulated_percent):
    if accumulated_percent <= 70:
        return "A"
    elif 70 < accumulated_percent <= 90:
        return "B"
    else:
        return "C"

# Применение функции присвоения категории к DataFrame
warehouse_product_df["category"] = warehouse_product_df[
    "accumulated_percent_profit_product_of_warehouse"
].apply(assign_category)

# Вывод результатов
print("Таблица продуктов:")
print(product_df)
print("\nТаблица заказов и прибыли:")
print(order_df)
print("\nСредняя прибыль:", average_profit)
print("\nТаблица продуктов и складов:")
print(warehouse_product_df)