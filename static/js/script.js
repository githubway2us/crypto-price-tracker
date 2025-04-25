let selectedCoins = [];

function addCoin() {
    const select = document.getElementById('coinSelect');
    const referencePriceInput = document.getElementById('referencePrice');
    const coin = select.value;
    const refPrice = parseFloat(referencePriceInput.value) || 0;

    if (coin && !selectedCoins.some(c => c.coin === coin)) {
        selectedCoins.push({ coin: coin, refPrice: refPrice });
        referencePriceInput.value = '';
        saveCoins(); // 👈 บันทึก
        updatePriceList();
    }
}

function removeCoin(coin) {
    selectedCoins = selectedCoins.filter(c => c.coin !== coin);
    saveCoins(); // 👈 บันทึก
    updatePriceList();
}

function updatePriceList() {
    const priceList = document.getElementById('priceList');
    priceList.innerHTML = '';

    selectedCoins.forEach(({ coin, refPrice }) => {
        fetch(`/get_price/${coin}`)
            .then(response => response.json())
            .then(data => {
                if (!data.error) {
                    const currentPrice = data.price;
                    const priceDiff = currentPrice - refPrice;
                    const percentDiff = refPrice ? (priceDiff / refPrice * 100) : 0;
                    const diffClass = priceDiff >= 0 ? 'price-diff-positive' : 'price-diff-negative';

                    const div = document.createElement('div');
                    div.className = 'coin-item';
                    div.innerHTML = `
                        <div>
                            <strong>${data.symbol}</strong><br>
                            ราคาปัจจุบัน: ${currentPrice.toFixed(4)} USDT<br>
                            ราคาอ้างอิง: ${refPrice.toFixed(4)} USDT<br>
                            <span class="${diffClass}">
                                ส่วนต่าง: ${priceDiff >= 0 ? '+' : ''}${priceDiff.toFixed(4)} USDT (${percentDiff.toFixed(2)}%)
                            </span>
                        </div>
                        <button class="remove-btn" onclick="removeCoin('${coin}')">×</button>
                    `;
                    priceList.appendChild(div);
                }
            });
    });
}

function saveCoins() {
    fetch('/save_coins', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ coins: selectedCoins })
    });
}

function loadCoins() {
    fetch('/load_coins')
        .then(response => response.json())
        .then(data => {
            if (!data.error) {
                selectedCoins = data;
                updatePriceList();
            }
        });
}

setInterval(updatePriceList, 5000);
loadCoins(); // โหลดเมื่อเริ่ม
