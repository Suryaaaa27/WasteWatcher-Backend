**♻️ WasteWatchers (WasteSense)**

Smart Waste Classification & Eco-Point Monitoring System

Built with Deep Learning + Computer Vision + Interactive Dashboard

---------------------------------------------------------------------------------------------

**🌍 Overview**

WasteWatchers (WasteSense) is an **AI-powered smart waste management system** that helps users identify waste type, locate the nearest disposal bins, and track their environmental impact through eco-points.

It combines:

✅ Deep Learning for waste classification

✅ Flask Backend for predictions & eco-point calculations

✅ Interactive Frontend (HTML, CSS, JS, Leaflet, Chart.js)

✅ User Dashboard showing eco-points, badges, leaderboard & graphs

This system is designed for campus deployments (Kalinga University) but is scalable to larger cities like Raipur.

--------------------------------------------------------------------------------------------------

**🔑 Features**

**📸 Snap or Upload Waste** – AI predicts waste type (Plastic, Organic, E-Waste, etc.)

**🗑️ Smart Disposal Guidance** – Suggests the nearest correct bin

**⚠️ Wrong Disposal Alert** – Notifies if waste is disposed in the wrong bin

**📍 Campus Bin Map** – Shows all bins inside Kalinga University using Leaflet maps

**🔥 Raipur Heatmap** – Tracks waste disposal locations citywide

**📊 Dashboard Analytics** – Eco-points vs Waste Disposed graph, badges, leaderboard

**🌱 Eco-Points System** – Rewards users for proper disposal

**🏆 Leaderboard**– Encourages competition among students

--------------------------------------------------------------------------------------------------

**🖼️ ScreenShots**
1: Landing Page- <img width="1919" height="858" alt="image" src="https://github.com/user-attachments/assets/19b0196e-97da-422a-945c-1f79553f5b60" />
2: Login Page- <img width="1915" height="882" alt="image" src="https://github.com/user-attachments/assets/36a7ad75-a35d-4e0b-93d2-f860c44d66d1" />
3: Camera and Waste Upload Page- <img width="1919" height="872" alt="image" src="https://github.com/user-attachments/assets/85b45018-e791-46ec-aba7-f2c048cea8e4" />
4: Waste Ananlysis- <img width="1888" height="854" alt="image" src="https://github.com/user-attachments/assets/79adcaa5-fa7c-4ca9-bc57-c5ff0338ab84" />
5: Map showing neaby Dispose- <img width="1919" height="857" alt="image" src="https://github.com/user-attachments/assets/806c863d-cbff-4480-9c29-331b73d65e37" />
6: Eco Points Page- <img width="1919" height="869" alt="image" src="https://github.com/user-attachments/assets/32b26a73-4c48-46e8-837b-81620f508cdd" />
7: Local Kabadiwala Collaboration- <img width="1919" height="813" alt="image" src="https://github.com/user-attachments/assets/7c211b45-c709-43a9-8d9b-5928b0579672" />
8: Eco Games Page- <img width="1919" height="860" alt="image" src="https://github.com/user-attachments/assets/c81af2ce-0939-4878-9b60-20a0747197df" />
9: Dashboard Page- <img width="1919" height="862" alt="image" src="https://github.com/user-attachments/assets/a5b2f31c-b00d-4216-ba57-3cff2aa71592" />
10: About Us- <img width="1919" height="878" alt="image" src="https://github.com/user-attachments/assets/468582bd-0538-4295-bcfc-f45a191b70fb" />

-------------------------------------------------------------------------------------------------

**🛠️ Tech Stack**

**Frontend:**

-HTML, CSS, JavaScript

-Leaflet.js (Maps)

-Chart.js (Graphs & Analytics)

**Backend:**

-Flask (Python)

-TensorFlow/Keras (Deep Learning Model)

-PIL, NumPy

**Database/Storage:**

-In-memory logs (extendable to SQLite/Postgres)

-------------------------------------------------------------------------------

**⚙️ Installation**

# Clone repository
git clone https://github.com/your-username/wastewatchers.git
cd wastewatchers

# Backend Setup
cd backend
pip install -r requirements.txt
python app.py

# Frontend
cd ../frontend
# Open intro.html in browser

-----------------------------------------------------------------------------------

**🔧 Requirements**

Flask
flask-cors
tensorflow
numpy
pillow

-----------------------------------------------------------------------------------

**🚀 Usage**

**Open intro.html** → Navigate to Snap Waste.

**Upload/Capture** a waste image.

System detects**waste type + suggests correct bin**.

**Dashboard (dashboard.html)** updates eco-points & graphs for logged-in user (e.g., Sneha).

-------------------------------------------------------------------------------------

**📊 Eco Points System**

| Waste Type | Eco Points per Item |
| ---------- | ------------------- |
| Organic    | 500                 |
| Plastic    | 150                 |
| E-Waste    | 200                 |
| Battery    | 120                 |
| Metal      | 180                 |
| Glass      | 100                 |

---------------------------------------------------------------------------------------

**📈 Graph: Eco Points vs Waste Disposed**

The dashboard visualizes eco-points earned vs waste disposed.

**🌱 Organic Waste** → Highest eco points (biogas & compost potential)

**⚡ E-Waste & Batteries** → Significant eco points (toxic leak prevention)

**🧃 Plastic & Glass** → Fewer points but reduces landfill load

**Insight**: The system motivates eco-sensitive waste disposal by rewarding higher eco-points.

----------------------------------------------------------------------------------------

**🌐 Scalability**

✅ Works at Kalinga University campus level

✅ Scalable to Raipur City with municipal bin mapping

✅ Extensible to nationwide waste monitoring

----------------------------------------------------------------------------------------

**🏆 Contribution**

Pull requests are welcome! If you'd like to contribute:

-Fork the repo

-Create a branch (feature-new)

-Commit changes

-Submit a PR 🎉

----------------------------------------------------------------------------------------

**👨‍💻 Authors**

1- **Sneha Khetan**: |Frontend Designer, UI/UX Developer|
                     |khetansneha214@gmail.com|
                     |Kalinga University|


                     
2- **Surya Kumar Srivastava**: |Backend Integrator, AIML Developer|
                               |srivastavasurya0111@gmail.com|
                               |Kalinga University|

----------------------------------------------------------------------------------------

**📜 License**

MIT License © 2025 WasteWatchers

----------------------------------------------------------------------------------------

*Our goal is to create a platform that not only detects waste but also rewards individuals for disposing it correctly. By gamifying the recycling process, we inspire people to keep coming back, learn more, and contribute to a cleaner, greener future.*


  
  
