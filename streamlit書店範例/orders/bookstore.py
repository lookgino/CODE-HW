import streamlit as st
from datetime import datetime
import pandas as pd
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import copy
import os
import json

#設定優惠
discount = 0.8

# 讀取設定檔
with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

import toml
from toml import TomlDecodeError

# 初始化身份驗證
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)
#global login
#login = 0

# 初始化使用者資訊
if "user_info" not in st.session_state:
    st.session_state.user_info = {
        "name": None,
        "shopping_cart": [],
        "order_history": []
    }

# 用戶訂單歷史檔案路徑
orders_path = "./orders/"

# 確保訂單目錄存在
if not os.path.exists(orders_path):
    os.makedirs(orders_path)

# 加載用戶訂單歷史
def load_user_order_history(username):
    order_history_file = f"{orders_path}/{username}.csv"
    if os.path.exists(order_history_file):
        return pd.read_csv(order_history_file)
    return pd.DataFrame(columns=["title", "quantity"])

# 保存用戶訂單歷史
def save_user_order_history(username, current_orders):
    order_history_file = f"{orders_path}/{username}.csv"
    if os.path.exists(order_history_file):
        # 如果檔案已存在，則讀取並附加新訂單
        existing_orders = pd.read_csv(order_history_file)
        updated_orders = pd.concat([existing_orders, pd.DataFrame(current_orders)], ignore_index=True)
    else:
        # 如果檔案不存在，則創建新的 DataFrame
        updated_orders = pd.DataFrame(current_orders)
    
    # 保存更新後的訂單歷史
    updated_orders.to_csv(order_history_file, index=False)



def login_page():
    # 在登入頁面以對話框的形式顯示用戶消息
    page =  st.sidebar.radio("選擇頁面", [  "商品總覽", "購物車","追蹤訂單", "歷史訂單", "留言板"])
    if page == "商品總覽":
        view_products()
    elif page == "歷史訂單":        
        order_history()
    elif page == "購物車":
        shopping_cart_page()
    elif page == "追蹤訂單":
        track_orders()
    elif page == "留言板":
        message_board()



import csv

csv_file_path = 'book.csv'

# 讀取CSV檔案，將資料存入DataFrame

books = pd.read_csv(csv_file_path)


# 初始化 session_state
if "shopping_cart" not in st.session_state:
    st.session_state.shopping_cart = []
# 初始化 session_state
if "track_list" not in st.session_state:
    st.session_state.track_list = []
# 定義各頁面
    
# 首頁
def home():
    st.title("書店店商系統")
    st.write("歡迎光臨書店店商系統！")


# 商品總覽
def view_products():
    st.title("商品總覽")

    for i in range(0, len(books)):
        st.write(f"## {books.at[i, 'title']}")
        st.image(books.at[i, "image"], caption=books.at[i, "title"], width=300)  
        st.write(f"**作者:** {books.at[i, 'author']}")
        st.write(f"**類型:** {books.at[i, 'genre']}")
        st.write(f"**金額:** {books.at[i, 'price']}")
        
        quantity = st.number_input(f"購買數量 {i}", min_value=1, value=1, key=f"quantity_{i}")
        quantity_track = st.number_input(f"團購數量 {i}", min_value=1, value=1, key=f"quantity_track_{i}")

        if st.button(f"購買 {books.at[i, 'title']}", key=f"buy_button_{i}"):
            if "shopping_cart" not in st.session_state:
                st.session_state.shopping_cart = []
            st.session_state.shopping_cart.append({
                "title": books.at[i, "title"],
                "quantity": quantity,
                "total_price" : int(books.at[i, 'price']) * int(quantity)  # Total price calculation
            })
            st.write(f"已將 {quantity} 本 {books.at[i, 'title']} 加入購物車")
        elif st.button(f"加入團購{books.at[i,'title']}",key=f"track_button_{i}"):
            track_payment( i, quantity_track)
        st.write("---")

#按下radio後會整個form不見

#押金介面    
def track_payment(g , q):
    with st.form(key="押金金額") as form:
        st.title("**押金規則**")
        quantity_track = int(q)
        book = g
        st.write("依照你所選的期望折扣會有相對應不同的押金，每次團購時長為3天，最終折扣若未達到期望，如不想購買，押金將全額退還；\n反之，如已達到期望，如最終還是決定不購買則沒收押金。\n購買時，押金將直接折抵結帳金額!")
        option = st.radio(
        '你期望的折扣？',
        ['9折', '85折', '8折', '75折'])
            
        付款方式 = st.selectbox('請選擇付款方式', ['信用卡', 'Line Pay'])
        優惠碼 = st.text_input('優惠代碼')
        寄送方式 = st.selectbox('請選擇寄送方式', ['寄送到府', '寄送至指定便利商店'])
        
        submitted = st.form_submit_button("確認付款")
        
        if submitted:
            if option == '9折':
                info = '**你所選的折扣，押金為' + str(30*quantity_track) + '元**'
            
            elif option == '85折':
                info = '**你所選的折扣，押金為' + str(50*quantity_track) + '元**'
            
            elif option == '8折':
                info = '**你所選的折扣，押金為' + str(80*quantity_track) + '元**'
            
            elif option == '75折':
                info = '**你所選的折扣，押金為' + str(100*quantity_track) + '元**'

            st.write(info)
            
            if "track_list" not in st.session_state:
                st.session_state.track_list = []
            st.session_state.track_list.append({
                "title": books.at[g, "title"],
                "quantity": quantity_track 
            })    
            st.write(f"已將 {quantity_track} 本 {books.at[g, 'title']} 加入追蹤清單")


# 顯示訂單
def display_order():
    st.title("訂單明細")

    # 顯示購物車中的商品
    for item in st.session_state.shopping_cart:
        st.write(f"{item['quantity']} 本 {item['title']}")
        total_expense = sum(item["total_price"] for item in st.session_state.shopping_cart)
    # 顯示追蹤清單中的商品
    for item in st.session_state.track_list:
        st.write(f"{item['quantity']} 本 {item['title']}")
        total_expense = sum(item["total_price"] for item in st.session_state.track_list)
    # 顯示其他訂單相關資訊，例如總金額、訂單時間等
    st.write(f"總金額: {total_expense}")

    order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.write(f"訂單時間: {order_time}")

# 購物車頁面
def shopping_cart_page():
    st.title("購物車")
    
    if not st.session_state.shopping_cart:
        st.write("購物車是空的，快去選購您喜歡的書籍吧！")
    else:
        # Create a Pandas DataFrame from the shopping cart data
        df = pd.DataFrame(st.session_state.shopping_cart)

        # Display the DataFrame as a table
        st.table(df)

        pay = st.button('結帳')

        if pay:
            st.session_state.show_payment = True
        if 'show_payment' in st.session_state and st.session_state.show_payment:
            Payment_page()


# 結帳頁面
def Payment_page():
    st.title("結帳")
    with st.form(key="購物清單") as form:
        購買詳情 = display_order()
        付款方式 = st.selectbox('請選擇付款方式', ['信用卡', 'Line Pay'])
        優惠碼 = st.text_input('優惠代碼')
        寄送方式 = st.selectbox('請選擇寄送方式', ['寄送到府', '寄送至指定便利商店'])
        
        submitted = st.form_submit_button("確認付款")
        
    if submitted:
        order_history_df = pd.DataFrame(st.session_state.shopping_cart)
            # 保存用戶訂單歷史
        save_user_order_history(st.session_state.user_info["name"], order_history_df)
        st.session_state.shopping_cart = []
        st.write("交易成功！")

# 留言頁
def message_board():
    # 初始化 session_state
    if "past_messages" not in st.session_state:
        st.session_state.past_messages = []

    # 在應用程式中以對話框的形式顯示用戶消息
    with st.chat_message("user"):
        st.write("歡迎來到留言板！")

    # 接收用戶輸入
    prompt = st.text_input("在這裡輸入您的留言")

    # 如果用戶有輸入，則將留言加入 session_state 中
    if prompt:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.past_messages.append({"user": "user", "message": f"{timestamp} - {prompt}"})

    # 留言板中顯示過去的留言
    with st.expander("過去的留言"):
        # 顯示每條留言
        for message in st.session_state.past_messages:
            with st.chat_message(message["user"]):
                st.write(message["message"])

def track_orders():
    st.title("追蹤清單")
    
    if not st.session_state.track_list:
        st.write("還沒加入任何團購，快去選購您喜歡的書籍吧！")
    else:
        # Create a Pandas DataFrame from the shopping cart data
        df = pd.DataFrame(st.session_state.track_list)

        # Display the DataFrame as a table
        st.table(df)
        
        pay = st.button('結帳')

        if pay:
            st.session_state.show_payment = True
        if 'show_payment' in st.session_state and st.session_state.show_payment:
            Payment_page()


# 訂單歷史頁面
def order_history():
    st.title("訂單歷史")
    # 將訂單資料轉換為 DataFrame
    df = load_user_order_history(st.session_state.user_info["name"])

    # 顯示表格
    st.table(df)

def main():
    
    st.title("書店店商系統")
    st.write("歡迎光臨書店店商系統！")   
    st.image("https://allez.one/wp-content/uploads/2022/04/%E9%9B%BB%E5%95%86%E7%B6%93%E7%87%9F1.jpg")
    st.session_state.login = False
    
    # 登入
    name, authentication_status, username = authenticator.login('Login', 'main')
    st.session_state.login = authentication_status
    if authentication_status:
        authenticator.logout('Logout', 'main')
        st.session_state.user_info["name"] = name
        # 加載用戶訂單歷史
        st.session_state.user_info["order_history"] = load_user_order_history(username)
        st.write(f'Welcome *{name}*')  
        login_page()
    elif authentication_status == False:
        st.error('Username/password is incorrect')
    elif authentication_status == None:
        st.warning('Please enter your username and password')

if __name__ == "__main__":
    main()



