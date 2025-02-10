# CODE-WEAVERS_AIPS08_-FinWise


🚀 FinWise - AI-Powered Personal Finance Assistant

👨‍💻 Team Name: CODE-WEAVERS                                                                                                   

🆔 Problem Statement ID (PSID): AIPS08

Project Description:
  
  FinWise is an AI-powered personal finance assistant that helps users manage their finances efficiently. The assistant provides personalized budgeting, expense     tracking, and savings recommendations. The project focuses on transaction classification using AI and delivers actionable insights for better financial control.   Currently, transactions are entered manually, but future versions will integrate with bank APIs for automation.

🎯 Objective

🔹 Automatically classify user transactions with high accuracy.

🔹 Provide personalized financial insights and saving recommendations based on spending patterns.

🔹 Ensure secure data handling and user privacy.

🔹 Deliver a real-time financial dashboard for visualizing expenses and tracking financial health.

✨ Key Features

📌 Transaction Classification and Budget Tracking                                                                                                    
  
📌 Categorizes manually entered transactions into predefined categories (e.g., 🍔 Food, 🚗 Transport, 🎭 Entertainment) using our ml model.                                                             
📌 Provides budget suggestions based on user spending history.

📌 Visualizes monthly expenses to help users stay on budget.

Example:

    💰 Input: "Rent - ₹15,000, Groceries - ₹3,000, Travel - ₹1,000"
    🤖 AI Output: "Your total monthly expenses so far are ₹19,000. You’re on track for your budget, but keep an eye on travel expenses."

2. 💡 Personalized Financial Insights and Recommendations

📌 Analyzes spending patterns to offer personalized saving tips.

📌 Suggests areas where users can cut expenses or allocate more funds for savings and investments.

📌 Provides investment suggestions tailored to user preferences (🔵 Conservative, 🟡 Balanced, 🔴 Aggressive).


3. 📊 Real-Time Financial Dashboard

📌 Interactive dashboard with expense summaries, spending trends, and savings progress.

📌 Real-time charts 📈 for better visualization of expenses and income.

📌 Allows users to set and track financial goals (e.g., ✈️ Travel Fund, 🏠 Emergency Fund).

🛠️ Technology Stack

    📝 Programming Language: Python                                                                                
  
    📦 Frameworks & Libraries: Flask, Pandas, Scikit-learn

    🎨 Front-End: HTML, CSS, JavaScript

    🤖 AI Models: Machine Learning (Random Forest Classifier for transaction classification)

    📊 Data Visualization: Matplotlib, Plotly

    🗄️ Database: SQLite (for storing user transactions and budget data)

⚙️ Implementation Details

    🖊️ Manual Transaction Input: Users manually enter transactions, which are categorized using a trained Random Forest Classifier model.

    🤖 AI-based Insights: The system analyzes spending patterns and generates actionable insights for budgeting and saving.

    📊 Dashboard: Provides a real-time, user-friendly interface for monitoring financial health and tracking goals.

    🔐 Data Security: Strong encryption methods ensure secure data storage and handling.

    📥 Setup and Installation

    🔧 Prerequisites                    
  

Ensure you have Python 3 installed on your system along with the following dependencies:

    pip install flask pandas scikit-learn matplotlib plotly sqlite3

🏃 Steps to Run the Project

  Clone the repository:

    git clone https://github.com/your-username/finwise.git
    cd finwise

  Run the application:

    python app.py

  Open your browser and go to:

    http://localhost:5000

📖 Usage Guide

    🔑 Login/Register: Create an account or log in using registered credentials.

    💰 Enter Salary and Expenses: Input monthly salary and manually add expenses.

    📊 View Expenses: Check categorized transactions and spending insights.

    📈 Get Investment Insights: Receive personalized recommendations for savings and investments.

    🚀 Future Enhancements

    🔄 Integration with bank APIs for automatic transaction import.

    🤖 More advanced AI models for improved transaction classification.

    📱 Mobile application support for better accessibility.

    🔐 Additional security features like two-factor authentication.

🤝 Contributors                    
  
Your Name 👨‍💻 Yash Kishor Patil

Teammate 1 👩‍💻:Arshiya Shaikh
Teammate 2 👨‍💻:Prerna Khatri                    

 Screenshots:
![image](https://github.com/user-attachments/assets/015ce63b-0076-4e56-9223-9a4f87842d76)
![image](https://github.com/user-attachments/assets/4e8b0e21-e22b-4142-9f2b-2473b0796627)

2) Add your name and salary

![image](https://github.com/user-attachments/assets/6a0e6246-d948-4bcc-b122-7b76033b2a34)

3) I) Add expenses – Since Open Banking APIs are not available, we have to manually add expenses as 
follows:

![image](https://github.com/user-attachments/assets/fe1f8e98-1852-48eb-9a10-79e80946ecbb)
![image](https://github.com/user-attachments/assets/79e40a57-9888-4daa-9d8d-eac5895c98fa)
![image](https://github.com/user-attachments/assets/c11aee72-3ef9-4e56-bac8-9218bb60b0a6)
![image](https://github.com/user-attachments/assets/99ae28bf-e792-4b1d-aa9c-a875c8fe5a62)

4) Get additional investment insights according to the Indian market in the investment suggestions.

![image](https://github.com/user-attachments/assets/00e9f28e-7725-4dee-aad9-d08c53fe6be1)
![image](https://github.com/user-attachments/assets/dbf643d1-38f3-4817-8c9c-8d6e429bd4b6)
![image](https://github.com/user-attachments/assets/9c8bca0d-d09e-4a25-9a5e-308fd6aaa9ec)
![image](https://github.com/user-attachments/assets/8af27356-1277-4364-8211-5dc086c7a745)

#ML Model for Classification of Transaction:

![image](https://github.com/user-attachments/assets/a76222e5-ccd7-4a71-b8ab-f5c4c3f42484)
![image](https://github.com/user-attachments/assets/0477f07f-a497-4f1b-8575-f25ea2d38caa)


📜 License

This project is licensed under the MIT License - see the LICENSE file for details.
  
