# Classical Music Catalogue System
A lightweight, interactive web-based classical music work cataloguing system built to address the maintenance and usability limitations of the traditional MerMEId system. This project parses MEI XML format data for classical music composers, provides structured data storage, multi-condition query, CSV export, and composer detail visualization, serving music researchers, enthusiasts, and cultural institutions.

## Project Overview
### Core Objectives
- Replace the complex Java-based MerMEId system with a **lightweight Python technical stack** (Flask + lxml + SQLite) to reduce maintenance costs by 90%.
- Realize structured processing and storage of MEI XML music catalogue data for **Carl Nielsen** and **Frederick Delius**.
- Provide user-friendly functions: multi-condition work query, genre/decade filtering, CSV data export, and composer detail data visualization.
- Expose standard RESTful APIs for flexible third-party integration, making up for the poor scalability of traditional systems.

### Key Features
✅ **MEI XML Data Crawling & Parsing**: Automated crawling of official composer MEI XML files, robust parsing with namespace support and data standardization.

✅ **Multi-Condition Query**: Filter works by keyword, music genre, and creation decade; real-time result rendering.

✅ **Data Export**: One-click export of query results to CSV (UTF-8 BOM encoded, compatible with Excel/Pandas).

✅ **Composer Detail Visualization**: View top 5 works, genre statistics, and creation decade distribution for each composer.

✅ **RESTful API Service**: Expose APIs for genre/decade acquisition, work query, and composer detail retrieval.

✅ **Cross-Browser Compatibility**: Support Chrome, Firefox, Edge with stable front-end interaction.

## Technical Stack
| Module               | Technology Stack                                                                 |
|----------------------|----------------------------------------------------------------------------------|
| **Data Crawling**    | Python 3.9+, Requests, BeautifulSoup4                                            |
| **XML Parsing**      | lxml (XPath namespace support, 5-10x faster than Python's built-in XML library)  |
| **Backend**          | Flask 2.3.3 (lightweight Web framework, RESTful API development)                  |
| **Database**         | SQLite 3 (file-based relational database, zero configuration)                     |
| **Frontend**         | HTML5, CSS3, Native JavaScript (no heavy frameworks, lightweight interaction)    |
| **Data Export**      | Python csv module, JavaScript Blob API (UTF-8 BOM encoding for Excel compatibility) |
| **Visualization**    | ECharts (composer decade distribution bar chart)                                  |

## Quick Start
### 1. Environment Preparation
- Install Python 3.9+ (add to PATH during installation)
- Verify Python & pip installation:
  ```bash
  python --version  # or python3 --version (macOS/Linux)
  pip --version     # or pip3 --version (macOS/Linux)
  ```
### 2. Clone & Install Dependencies
```bash
# Clone the repository (replace with your actual repo URL)
git clone [your-repo-url].git
cd classical-music-catalogue

# Install all dependencies
pip install -r requirements.txt
# Accelerated installation (China mirror)
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```
### 3. Start the System
```bash
# Run Flask backend server
python app.py
```
The server starts at the default address: http://127.0.0.1:5000
Open the address in a browser to access the work query page; click the composer link to enter the composer detail page.