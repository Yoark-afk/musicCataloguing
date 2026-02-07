from flask import Flask, render_template, jsonify, request
from database import *

app = Flask(__name__)


@app.route('/')
def index():
    """Render the home page (index.html)"""
    return render_template('index.html')


@app.route('/composer-detail')
def composer_detail():
    """Render the composer detail page (composer-detail.html)"""
    return render_template('composer-detail.html')


@app.route('/api/genres')
def get_genres():
    """Get all unique music work genres from the database, sorted alphabetically"""
    try:
        all_works = get_all_works()
        genres = []
        for work in all_works:
            genres.extend(work.genre.split(','))
        # Deduplicate and sort genres
        genres = sorted(list(set(genres)))
        return jsonify(genres)
    except Exception as e:
        return jsonify({'error': f'Server error when fetching genres: {str(e)}'}), 500


@app.route('/api/decades')
def get_decades():
    """Get all unique creation decades of works from the database, sorted numerically"""
    try:
        all_works = get_all_works()
        decades = []
        for work in all_works:
            decades.append(work.decade)
        # Deduplicate and sort decades
        decades = sorted(list(set(decades)))
        return jsonify(decades)
    except Exception as e:
        return jsonify({'error': f'Server error when fetching decades: {str(e)}'}), 500


@app.route('/api/works')
def get_works():
    """
    Get filtered music works by keyword/genre/decade
    Support fuzzy search for title/composer, exact match for decade, fuzzy match for genre
    """
    # Get request parameters (default values set for non-required fields)
    keyword = request.args.get('keyword', '').lower()
    type_filter = request.args.get('type', 'all')  # all = no genre filter
    decade_filter = request.args.get('decade', 'all')  # all = no decade filter
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Base query with join between works and composers table
        query = '''
                SELECT w.*, c.name as composer 
                FROM works w
                JOIN composers c ON w.composer_id = c.composer_id
                WHERE 1=1
            '''
        params = []
        # Fuzzy search by work title or composer name
        if keyword:
            query += '''
                    AND (w.title LIKE ? OR c.name LIKE ?)
                '''
            params.extend([f'%{keyword}%', f'%{keyword}%'])
        # Fuzzy filter by work genre (if not 'all')
        if type_filter != 'all':
            query += ' AND w.genre like ?'
            params.append(f'%{type_filter}%')
        # Exact filter by creation decade (if not 'all')
        if decade_filter != 'all':
            query += ' AND w.decade = ?'
            params.append(decade_filter)
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        works = []
        # Format rows to Work object list and convert to dict
        for row in rows:
            work = Work(
                work_id=row['work_id'],
                composer_id=row['composer_id'],
                title=row['title'],
                genre=row['genre'],
                creation_year=row['creation_year'],
                detail_url=row['detail_url'],
                composer=row['composer'],
                decade=row['decade']
            )
            works.append(work.to_dict())
        return jsonify(works)
    except Exception as e:
        return jsonify({'error': f'Server error when fetching filtered works: {str(e)}'}), 500


@app.route('/api/composers')
def get_composers():
    """Get all composers (ID + name) from database, sorted by name alphabetically"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Query composer ID and name, sorted by name
        cursor.execute('SELECT composer_id, name FROM composers ORDER BY name ASC')
        composers = cursor.fetchall()
        conn.close()

        # Format to front-end compatible list
        composer_list = []
        for composer in composers:
            composer_list.append({
                'id': composer['composer_id'],
                'name': composer['name']
            })
        return jsonify(composer_list)
    except Exception as e:
        return jsonify({'error': f'Server error when fetching composer list: {str(e)}'}), 500


def row_to_dict(row):
    """Convert a single sqlite3.Row object to a standard Python dictionary"""
    if not row:
        return None
    return dict(row)


def rows_to_list(rows):
    """Convert a list of sqlite3.Row objects to a list of standard Python dictionaries"""
    if not rows:
        return []
    return [dict(row) for row in rows]


@app.route('/api/composers/<int:composer_id>')
def get_composer_detail(composer_id):
    """
    Get detailed information of a specific composer by ID
    Include basic info, top 5 works, genre statistics, work count distribution by decade
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Query basic composer info (ID + name)
        cursor.execute('''
            SELECT c.composer_id, c.name
            FROM composers c
            WHERE c.composer_id = ?
        ''', (composer_id,))
        composer = cursor.fetchone()
        if not composer:
            conn.close()
            return jsonify({'error': f'Composer with ID {composer_id} not found'}), 404

        # 2. Query top 5 representative works (sorted by creation year)
        cursor.execute('''
            SELECT title, creation_year as create_year
            FROM works
            WHERE composer_id = ?
            ORDER BY creation_year ASC
            LIMIT 5
        ''', (composer_id,))
        represent_works = rows_to_list(cursor.fetchall())
        # 3. Query work genre statistics (group by genre, count works)
        cursor.execute('''
            SELECT genre, COUNT(*) as count
            FROM works
            WHERE composer_id = ?
            GROUP BY genre
        ''', (composer_id,))

        genre_stats = rows_to_list(cursor.fetchall())
        genre_stat_dict = {item['genre']: item['count'] for item in genre_stats}
        print(4)
        # 4. Query work count distribution by decade (group by decade, count works)
        cursor.execute('''
            SELECT decade, COUNT(*) as count
            FROM works
            WHERE composer_id = ?
            GROUP BY decade
            ORDER BY decade ASC
        ''', (composer_id,))
        year_distributions = rows_to_list(cursor.fetchall())
        year_dist_dict = {item['decade']: item['count'] for item in year_distributions}
        conn.close()

        # Assemble final detail data (front-end compatible format)
        composer_detail = {
            'id': composer['composer_id'],
            'name': composer['name'],
            'represent_works': represent_works,
            'genre_stat': genre_stat_dict,
            'year_distribution': year_dist_dict
        }
        return jsonify(composer_detail)
    except Exception as e:
        return jsonify({'error': f'Server error when fetching composer detail: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True)
