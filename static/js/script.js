// DOM Element Acquisition
const keywordInput = document.getElementById('keyword-input');
const typeSelect = document.getElementById('type-select');
const decadeSelect = document.getElementById('decade-select');
const filterBtn = document.getElementById('filter-btn');
const resultList = document.getElementById('result-list');
const resultCount = document.getElementById('result-count');
const sortSelect = document.getElementById('sort-select');
const exportCsvBtn = document.getElementById('export-csv-btn');

// Initialize Page
window.onload = async () => {
    await loadFilterOptions();
    // Bind click event for filter button
    filterBtn.addEventListener('click', fetchFilteredWorks);
    // Support Enter key to trigger filtering
    keywordInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') fetchFilteredWorks();
    });
    // Add sort menu event
    sortSelect.addEventListener('change', () => {
        // Filtered works already exist, sort and re-render directly
        if (window.filteredWorks) {
            const sortedWorks = sortWorks(window.filteredWorks);
            renderResults(sortedWorks);
        }
    });
    exportCsvBtn.addEventListener('click', exportToCsv);
    await fetchFilteredWorks();

    const composerTags = document.querySelectorAll('.composer-tag');
    composerTags.forEach(tag => {
        tag.addEventListener('click', function() {
            const composerId = this.dataset.composerId;
            window.location.href = `composer-detail.html?id=${composerId}`;
        });
    });
    loadComposerList();
};

async function loadComposerList() {
    try {
        const response = await fetch('/api/composers');
        const composers = await response.json();
        const composerTagsContainer = document.getElementById('composer-tags');
        composerTagsContainer.innerHTML = '';

        composers.forEach(composer => {
            const tag = document.createElement('span');
            tag.className = 'composer-tag';
            tag.dataset.composerId = composer.id;
            tag.textContent = composer.name;
            tag.addEventListener('click', function() {
            const composerId = this.dataset.composerId
            window.location.href = `composer-detail?id=${composerId}`;
        });
            composerTagsContainer.appendChild(tag);
        });
    } catch (error) {
        console.error('Failed to load composer list: ', error);
        document.getElementById('composer-tags').innerHTML = '<span class="composer-tag">Load failed</span>';
    }
}

async function loadFilterOptions() {
    try {
        // Load work genres
        const genreRes = await fetch('/api/genres');
        const genres = await genreRes.json();
        genres.forEach(genre => {
            const option = document.createElement('option');
            option.value = genre;
            option.textContent = genre;
            typeSelect.appendChild(option);
        });

        // Load creation decades
        const decadeRes = await fetch('/api/decades');
        const decades = await decadeRes.json();
        decades.forEach(decade => {
            const option = document.createElement('option');
            option.value = decade;
            option.textContent = decade;
            decadeSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Failed to load filter options: ', error);
        alert('Failed to load filter options, please refresh the page!');
    }
}

// Export to CSV File
function exportToCsv() {
    if (!window.filteredWorks || window.filteredWorks.length === 0) {
        alert('No data to export!');
        return;
    }

    // Get currently sorted work list
    const sortedWorks = sortWorks(window.filteredWorks);

    // 1. Define CSV headers
    const headers = [
        'Work ID',
        'Composer',
        'Title',
        'Genre',
        'Creation Year',
        'Detail URL',
        'Decade'
    ];

    // 2. Convert work data to CSV rows
    const csvRows = [
        headers.join(','), // Header row
        // Data rows (wrap with double quotes to handle commas and line breaks)
        ...sortedWorks.map(work => [
            `"${work.work_id}"`,
            `"${work.composer}"`,
            `"${work.title}"`,
            `"${work.genre}"`,
            `"${work.creation_year}"`,
            `"${work.detail_url}"`,
            `"${work.decade}"`
        ].join(','))
    ];

    // 3. Splice CSV content (add BOM to solve Chinese garbled code)
    // Note: Keep BOM for UTF-8 compatibility even for English
    const csvContent = '\uFEFF' + csvRows.join('\n');

    // 4. Create Blob and download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    // Custom file name (with timestamp)
    link.setAttribute('download', `WorkList_${new Date().toLocaleString().replace(/[/: ]/g, '-')}.csv`);
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

// Sort Work List
function sortWorks(works) {
    const sortType = sortSelect.value;
    let sortedWorks = [...works]; // Copy array to avoid modifying original data

    switch (sortType) {
        case 'title_asc':
            // Sort by work title in ascending order (alphabetical)
            sortedWorks.sort((a, b) => a.title.localeCompare(b.title));
            break;
        case 'title_desc':
            // Sort by work title in descending order
            sortedWorks.sort((a, b) => b.title.localeCompare(a.title));
            break;
        case 'decade_asc':
            // Sort by creation decade in ascending order
            sortedWorks.sort((a, b) => {
                // Extract decade number
                const decadeA = parseInt(a.decade);
                const decadeB = parseInt(b.decade);
                return decadeA - decadeB;
            });
            break;
        case 'decade_desc':
            // Sort by creation decade in descending order
            sortedWorks.sort((a, b) => {
                const decadeA = parseInt(a.decade);
                const decadeB = parseInt(b.decade);
                return decadeB - decadeA;
            });
            break;
        default:
            // Default sort by title in ascending order
            sortedWorks.sort((a, b) => a.title.localeCompare(b.title));
    }

    return sortedWorks;
}

// Request filtered work data from backend
async function fetchFilteredWorks() {
    // Build filter parameters
    const params = {
        keyword: keywordInput.value.trim(),
        type: typeSelect.value,
        decade: decadeSelect.value
    };

    try {
        // Send GET request to backend API
        const response = await fetch(`/api/works?${new URLSearchParams(params)}`);
        if (!response.ok) throw new Error('Request failed');

        const data = await response.json();
        // Save original filtered data (for subsequent sorting)
        window.filteredWorks = data;
        // Sort first (default title ascending), then render
        const sortedWorks = sortWorks(data);
        renderResults(sortedWorks);
        exportCsvBtn.disabled = data.length === 0;
    } catch (error) {
        console.error('Filter request error: ', error);
        resultList.innerHTML = '<div class="empty-state">Filter failed, please try again</div>';
        resultCount.textContent = 'Total 0 results';
    }
}

// Render Result List
function renderResults(works) {
    // Update result count
    resultCount.textContent = `Total ${works.length} results`;

    if (works.length === 0) {
        resultList.innerHTML = '<div class="empty-state">No matching works</div>';
        return;
    }
    resultList.innerHTML = works.map(work => `
        <a href="${work.detail_url}" class="work-card-link" target="_blank" rel="noopener noreferrer">
            <div class="work-card">
                <h3>${work.title}</h3>
                <div class="info-row"><strong>Genre: </strong>${work.genre}</div>
                <div class="info-row"><strong>Creation Year：</strong>${work.creation_year}</div>
                <div class="info-row"><strong>Composer：</strong>${work.composer}</div>
            </div>
        </a>
    `).join('');
}