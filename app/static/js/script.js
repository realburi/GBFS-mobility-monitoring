let chart;
const colors = ['#8884d8', '#82ca9d', '#ffc658'];

function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return `${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`;
}

function processData(data, selectedMetric) {
    const cities = [...new Set(data.map(item => item.city))];
    const processedData = {};
    
    cities.forEach(city => {
        processedData[city] = {
            label: city,
            data: [],
            borderColor: colors[cities.indexOf(city) % colors.length],
            fill: false
        };
    });

    data.forEach(item => {
        const timestamp = formatTimestamp(item.timestamp);
        const value = selectedMetric === 'current_range_km' 
            ? Number(item.current_range_meters) / 1000000 
            : Number(item[selectedMetric]);
        
        processedData[item.city].data.push({x: timestamp, y: value});
    });

    return Object.values(processedData);
}

function createChart(data, selectedMetric) {
    console.log(data)
    const ctx = document.getElementById('dataChart').getContext('2d');
    
    if (chart) {
        chart.destroy();
    }

    chart = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: processData(data, selectedMetric)
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    type: 'category',
                    title: {
                        display: true,
                        text: 'Time'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: getYAxisLabel(selectedMetric)
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'QuestDB Multi-City Data Visualization'
                }
            }
        }
    });
}

function getYAxisLabel(metric) {
    switch(metric) {
        case 'current_range_km':
            return 'Range (km)';
        case 'is_disabled_count':
            return 'Disabled Count';
        case 'is_reserved_count':
            return 'Reserved Count';
        default:
            return '';
    }
}

function updateChart() {
    const selectedMetric = document.getElementById('metric-select').value;
    fetch('/api/data')
        .then(response => response.json())
        .then(data => createChart(data, selectedMetric));
}

document.addEventListener('DOMContentLoaded', () => {
    updateChart();
    document.getElementById('metric-select').addEventListener('change', updateChart);
});