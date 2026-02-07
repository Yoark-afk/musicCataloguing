document.addEventListener('DOMContentLoaded', function() {
    // Get composer ID from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const composerId = urlParams.get('id');

    if (!composerId) {
        alert('No composer ID specified');
        window.location.href = 'index.html'; // Redirect to home page
        return;
    }

    // Load composer detail data
    loadComposerDetail(composerId);
});

// Load composer details from API
async function loadComposerDetail(composerId) {
    try {
        const response = await fetch(`/api/composers/${composerId}`);
        if (!response.ok) throw new Error('Request failed');

        const composerData = await response.json();
        // Render basic info
        renderBasicInfo(composerData);
        // Render genre statistics
        renderGenreStat(composerData.genre_stat);
        // Render representative works
        renderRepresentWorks(composerData.represent_works);
        // Render work count distribution bar chart by decade
        renderYearChart(composerData.year_distribution);

    } catch (error) {
        console.error('Failed to load composer details: ', error);
        alert('Failed to load composer information, please try again');
    }
}

// Render basic information
function renderBasicInfo(data) {
    document.title = `${data.name} - Composer Details`;
    document.getElementById('composer-name').textContent = data.name;
}

// Render work genre statistics
function renderGenreStat(genreStat) {
    const genreListContainer = document.getElementById('genre-stat-list');
    genreListContainer.innerHTML = '';

    Object.entries(genreStat).forEach(([genre, count]) => {
        const genreItem = document.createElement('div');
        genreItem.className = 'genre-item';
        genreItem.innerHTML = `<span>${count}</span> ${genre} works`;
        genreListContainer.appendChild(genreItem);
    });
}

// Render representative works
function renderRepresentWorks(works) {
    const worksListContainer = document.getElementById('represent-works-list');
    worksListContainer.innerHTML = '';

    works.forEach(work => {
        const workItem = document.createElement('div');
        workItem.className = 'work-item';
        workItem.innerHTML = `
            <h4 class="work-title">${work.title}</h4>
            <p class="work-year">Creation Year: ${work.create_year}</p>
        `;
        worksListContainer.appendChild(workItem);
    });
}

// Render work count distribution bar chart by decade
function renderYearChart(yearDistribution) {
    const chartDom = document.getElementById('work-year-chart');
    const myChart = echarts.init(chartDom);

    // Process chart data
    const xAxisData = Object.keys(yearDistribution);
    const yAxisData = Object.values(yearDistribution);

    const option = {
        title: {
            text: 'Work Count Distribution by Decade',
            left: 'center',
            textStyle: { fontSize: 16 }
        },
        xAxis: {
            type: 'category',
            data: xAxisData,
            axisLabel: { rotate: 30 }
        },
        yAxis: {
            type: 'value',
            name: 'Number of Works'
        },
        series: [{
            data: yAxisData,
            type: 'bar',
            itemStyle: { color: '#007bff' },
            label: {
                show: true,
                position: 'top'
            }
        }],
        tooltip: {
            trigger: 'axis',
            formatter: '{b}: {c} works'
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '15%',
            top: '10%',
            containLabel: true
        }
    };

    myChart.setOption(option);
    // Adapt to window size
    window.addEventListener('resize', () => myChart.resize());
}