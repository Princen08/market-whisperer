const stockInput = document.getElementById('stockInput');
const addBtn = document.getElementById('addBtn');
const stockList = document.getElementById('stockList');
const listenBtn = document.getElementById('listenBtn');
const resultsSection = document.getElementById('resultsSection');

// Load initial stocks
fetchStocks();

addBtn.addEventListener('click', addStock);
stockInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') addStock();
});

listenBtn.addEventListener('click', analyzeMarket);

async function fetchStocks() {
    const res = await fetch('/stocks');
    const stocks = await res.json();
    renderTags(stocks);
}

async function addStock() {
    const symbol = stockInput.value.trim().toUpperCase();
    if (!symbol) return;

    try {
        const res = await fetch('/stocks', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symbol })
        });

        if (res.ok) {
            stockInput.value = '';
            fetchStocks();
        } else {
            const err = await res.json();
            alert(err.detail);
        }
    } catch (e) {
        console.error(e);
    }
}

async function removeStock(symbol) {
    await fetch(`/stocks/${symbol}`, { method: 'DELETE' });
    fetchStocks();
}

function renderTags(stocks) {
    stockList.innerHTML = stocks.map(stock => `
        <div class="tag">
            ${stock.symbol}
            <span class="remove" onclick="removeStock('${stock.symbol}')">&times;</span>
        </div>
    `).join('');
}

async function analyzeMarket() {
    listenBtn.textContent = "LISTENING...";
    listenBtn.disabled = true;
    resultsSection.innerHTML = '';

    try {
        // Start task
        const startRes = await fetch('/analyze/start', { method: 'POST' });
        const startData = await startRes.json();
        const taskId = startData.task_id;

        // Poll for results
        pollResults(taskId);
    } catch (e) {
        console.error(e);
        resultsSection.innerHTML = '<p style="text-align:center; color:var(--danger-color)">Failed to start analysis.</p>';
        listenBtn.textContent = "LISTEN TO THE MARKET";
        listenBtn.disabled = false;
    }
}

async function pollResults(taskId) {
    const pollInterval = setInterval(async () => {
        try {
            const res = await fetch(`/analyze/status/${taskId}`);
            const data = await res.json();

            if (data.state === 'SUCCESS') {
                clearInterval(pollInterval);
                renderWhispers(data.result);
                listenBtn.textContent = "LISTEN TO THE MARKET";
                listenBtn.disabled = false;
            } else if (data.state === 'FAILURE') {
                clearInterval(pollInterval);
                resultsSection.innerHTML = `<p style="text-align:center; color:var(--danger-color)">Analysis failed: ${data.error}</p>`;
                listenBtn.textContent = "LISTEN TO THE MARKET";
                listenBtn.disabled = false;
            } else {
                // Still pending, maybe update UI with a spinner or text
                listenBtn.textContent = "ANALYZING...";
            }
        } catch (e) {
            clearInterval(pollInterval);
            console.error(e);
            listenBtn.textContent = "LISTEN TO THE MARKET";
            listenBtn.disabled = false;
        }
    }, 2000); // Poll every 2 seconds
}

function renderWhispers(whispers) {
    if (whispers.length === 0) {
        resultsSection.innerHTML = '<p style="text-align:center; color:var(--text-secondary); grid-column: 1/-1;">The market is silent... for now.</p>';
        return;
    }

    resultsSection.innerHTML = whispers.map((w, index) => `
        <div class="whisper-card" style="animation-delay: ${index * 0.1}s">
            <div class="card-header">
                <span class="stock-symbol">${w.symbol}</span>
                <span class="severity-badge severity-${w.severity}">${w.type}</span>
            </div>
            <p class="message">${w.message}</p>
            <p class="reasoning"><strong>Analysis:</strong> ${w.reasoning}</p>
            <span class="action-badge action-${w.action}">${w.action}</span>
        </div>
    `).join('');
}
