// WebSocket을 통해 ML서버 연결
const serverWebSocket = new WebSocket("wss://14.32.188.229:8765");

serverWebSocket.onopen = () => {
console.log("Connected to the server WebSocket");
};

serverWebSocket.onmessage = (event) => {
    try {
        const data = JSON.parse(event.data);

        // 데이터가 예상하는 형식인지 확인
        if (data.timestamp && data.predicted_price) {
            const time = new Date(data.timestamp).toLocaleTimeString();
            const predictedPrice = data.predicted_price;

            // 데이터 업데이트
            cumulativeData.push({ time });
            predictedData.push({
                time,
                price: predictedPrice
            });

            // 차트 업데이트
            updateChart();
        } else {
            console.warn("Received unexpected data format:", data);
        }
    } catch (error) {
        console.error("Error processing WebSocket message:", error);
    }
};

serverWebSocket.onerror = (error) => {
    console.error("WebSocket error:", error);
};

serverWebSocket.onclose = () => {
    console.log("WebSocket connection closed");
};

//------------------------------------------------------------------

document.addEventListener("DOMContentLoaded", async function () {
    initializeWebSocketConnections();
    initializeUIElements();
    setInterval(fetchBalances, 1000); // 1초마다 잔고 업데이트 
    const initialArticles = await fetchBitcoinNews();
    updateNewsTable(initialArticles);
    setInterval(async () => {
        const newsArticles = await fetchBitcoinNews();
        updateNewsTable(newsArticles);
    }, 10000); // 10초마다 뉴스 업데이트
});

// 실시간 시장 데이터에 대한 WebSocket 연결
function initializeWebSocketConnections() {
    // Upbit WebSocket 설정
    const upbitWebSocket = new WebSocket("wss://api.upbit.com/websocket/v1");

    // KRW-BTC 티커, 호가창, 거래에 대한 구독
    upbitWebSocket.onopen = () => {
        const payload = [
            { "ticket": "test" },
            { "type": "ticker", "codes": ["KRW-BTC"] },
            { "type": "orderbook", "codes": ["KRW-BTC"] },
            { "type": "trade", "codes": ["KRW-BTC"] }
        ];
        upbitWebSocket.send(JSON.stringify(payload));
    };

    // 들어오는 메시지 처리
    upbitWebSocket.onmessage = async (event) => {
        const reader = new FileReader();
        reader.onload = function () {
            const data = JSON.parse(reader.result);
            if (data.type === "ticker") {
                currentBitcoinPrice = data.trade_price; // 실시간 비트코인 시세를 업데이트
                updateTickerData(data);
                updateChartData(data);
            } else if (data.type === "orderbook") {
                updateOrderBookData(data);
            } else if (data.type === "trade") {
                updateTradeData(data);
            }
        };
        reader.readAsText(event.data);
    };

    upbitWebSocket.onerror = (error) => {
        console.error("WebSocket error:", error);
    };

    upbitWebSocket.onclose = () => {
        console.warn("WebSocket closed. Reconnecting...");
        initializeWebSocketConnections(); // 연결이 끊어지면 다시 연결
    };

    // bitFlyer WebSocket 설정
    const bitflyerWebSocket = new WebSocket("wss://ws.lightstream.bitflyer.com/json-rpc");
    bitflyerWebSocket.onopen = () => {
        bitflyerWebSocket.send(JSON.stringify({
            method: "subscribe",
            params: { channel: "lightning_ticker_BTC_JPY" },
            id: 1
        }));
    };

    bitflyerWebSocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.params && data.params.message) {
            const price = data.params.message.ltp;
            document.getElementById("bitflyer-price").textContent = `${(price * 10).toLocaleString()} KRW`; // JPY-KRW 환율 적용 (10 가정)
        }
    };

    // Binance WebSocket 설정
    const binanceWebSocket = new WebSocket("wss://stream.binance.com:9443/ws/btcusdt@ticker");
    binanceWebSocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        const price = parseFloat(data.c);
        document.getElementById("binance-price").textContent = `${(price * 1400).toLocaleString()} KRW`; // USD-KRW 환율 적용 (1400 가정)
    };

    const okxWebSocket = new WebSocket("wss://ws.okx.com:8443/ws/v5/public");

    // WebSocket 연결이 열리면 구독 요청 전송
    okxWebSocket.onopen = () => {
        console.log("WebSocket 연결 성공");
        const subscribeMessage = JSON.stringify({
            op: "subscribe",
            args: [
                {
                    channel: "tickers",
                    instId: "BTC-USDT", // 비트코인/USDT 거래쌍
                },
            ],
        });
        okxWebSocket.send(subscribeMessage);
        console.log("구독 메시지 전송");
    };

    // WebSocket에서 메시지 수신
    okxWebSocket.onmessage = (event) => {
        const response = JSON.parse(event.data);
        if (response.event === "subscribe") {
            console.log("구독 성공:", response);
        } else if (response.arg && response.arg.channel === "tickers") {
            const tickerData = response.data[0];
            const price = parseFloat(tickerData.last);
            const krwPrice = price * 1400;
            document.getElementById("okx-price").textContent = `${krwPrice.toLocaleString()} KRW`;
        }
    };

    // WebSocket 오류 처리
    okxWebSocket.onerror = (error) => {
        console.error("WebSocket 오류:", error);
    };

    // WebSocket 연결 종료 처리
    okxWebSocket.onclose = () => {
        console.log("WebSocket 연결 종료");
    };
}

// 페이지의 티커 데이터를 업데이트하는 함수
function updateTickerData(data) {
    document.querySelector(".current-price").textContent = `${data.trade_price.toLocaleString()} KRW`;
    document.querySelector(".change-percent").textContent = `${(data.signed_change_rate * 100).toFixed(2)}%`;
    document.querySelector(".change-amount").textContent = `${data.signed_change_price > 0 ? "▲ " : "▼ "}${data.signed_change_price.toLocaleString()}`;
    document.querySelector(".volume").textContent = `${data.acc_trade_volume_24h.toFixed(3)} BTC`;
    document.querySelector(".trade-amount").textContent = `${data.acc_trade_price_24h.toLocaleString()} KRW`;

    // 가격 요소의 색상을 가격 변동에 따라 업데이트
    const priceElement = document.querySelector(".current-price");
    priceElement.style.color = data.signed_change_price > 0 ? "#28a745" : "#dc3545";
}

// 페이지의 호가 데이터를 업데이트하는 함수
function updateOrderBookData(data) {
    const orderbookBody = document.getElementById("special-orderbook-body");
    orderbookBody.innerHTML = "";

    const maxVolume = Math.max(...data.orderbook_units.map((item) => Math.max(item.ask_size, item.bid_size)));

    data.orderbook_units.forEach((item, index) => {
        const type = index < data.orderbook_units.length / 2 ? "매도" : "매수";
        const price = type === "매도" ? item.ask_price : item.bid_price;
        const volume = type === "매도" ? item.ask_size : item.bid_size;

        const percentage = (volume / maxVolume) * 100;

        const row = `
            <tr style="background-color: ${type === "매수" ? "rgba(40, 167, 69, 0.1)" : "rgba(220, 53, 69, 0.1)"};">
                <td style="font-weight: bold; color: ${type === "매수" ? "#28a745" : "#dc3545"};">${price.toLocaleString()}</td>
                <td>${volume.toFixed(3)}</td>
                <td style=" text-align: right;">${(price * volume).toLocaleString()}</td>
                <td style="width: 100px; text-align: left;">
                    <div style="height: 20px; background-color: ${type === "매수" ? "#28a745" : "#dc3545"}; width: ${percentage}%;"></div>
                </td>
            </tr>
        `;

        orderbookBody.innerHTML += row;
    });
}

// 페이지의 거래 데이터를 업데이트하는 함수
function updateTradeData(data) {
    const tradeBody = document.getElementById("trade-history-body");
    if (tradeBody) {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${new Date(data.timestamp).toLocaleTimeString()}</td>
            <td style="color: ${data.ask_bid === "ASK" ? "#dc3545" : "#28a745"}; font-weight: bold;">${data.trade_price.toLocaleString()}</td>
            <td>${data.trade_volume.toFixed(3)}</td>
        `;
        tradeBody.insertBefore(row, tradeBody.firstChild);
    }
}

// 차트 데이터를 업데이트하는 함수
let btcChart;
function updateChartData(data) {
    if (!btcChart) {
        const ctx = document.getElementById("btcChart").getContext("2d");
        btcChart = new Chart(ctx, {
            type: "line",
            data: {
                labels: [],
                datasets: [
                    {
                        label: "비트코인 가격 (KRW)",
                        data: [],
                        borderColor: "rgba(54, 162, 235, 1)",
                        borderWidth: 2,
                        tension: 0.4, // 부드러운 곡선
                        pointRadius: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: "시간"
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: "가격 (KRW)"
                        }
                    }
                }
            }
        });
    }
    btcChart.data.labels.push(new Date(data.timestamp).toLocaleTimeString());
    btcChart.data.datasets[0].data.push(data.trade_price);
    btcChart.update();
}

// UI 요소 초기화
function initializeUIElements() {
    // 슬라이더 및 페이지 상의 UI 초기화 관련 코드
    const ThresholdSlider = document.getElementById("Threshold-slider");
    const hiddenThresholdLevel = document.getElementById("hidden-Threshold-level");
    const ThresholdLevelDisplay = document.getElementById("Threshold-level-display");

    function updateThresholdLevelDisplay(value) {
        if (value != 10) {
            ThresholdLevelDisplay.textContent = "0.0" + value + "%";
            hiddenThresholdLevel.value = parseFloat("0.000" + value);
        } else {
            ThresholdLevelDisplay.textContent = "0.1%";
            hiddenThresholdLevel.value = 0.001;
        }
    }

    ThresholdSlider.addEventListener("input", (e) => {
        updateThresholdLevelDisplay(e.target.value);
    });
    updateThresholdLevelDisplay(ThresholdSlider.value);
}

// fetchBalances 함수에서 실시간 비트코인 시세를 반영
function fetchBalances() {
    fetch('/api/tradebalances')
        .then(response => {
            if (!response.ok) {
                throw new Error("Error fetching balances: " + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            const totalValueElement = document.getElementById('total-value');
            const ProfitValueElement = document.getElementById('profit-loss');
            const BTCValueElement = document.getElementById('BTC-value');
            const KRWValueElement = document.getElementById('KRW-value');
            
            let totalValue = 0;
            let profitValue = 0;
            let baseValue = 0;
            let BTCValue = 0;
            let KRWValue = 0;

            data.forEach(balance => {
                // Calculate total value
                if (balance.currency === 'BTC') {
                    BTCValue = parseFloat(balance.balance) * currentBitcoinPrice;
                    totalValue += parseFloat(balance.balance) * currentBitcoinPrice;
                    baseValue += parseFloat(balance.balance) * parseFloat(balance.avg_buy_price);
                } else if (balance.currency === 'KRW') {
                    KRWValue = parseFloat(balance.balance);
                    totalValue += parseFloat(balance.balance);
                    baseValue += parseFloat(balance.balance)
                }
            });
            profitValue = totalValue - baseValue;

            // Update total value in the DOM
            totalValueElement.textContent = `${totalValue.toFixed(2).toLocaleString()} KRW`;
            if (profitValue >= 0){
                ProfitValueElement.textContent = `+ ${profitValue.toFixed(2).toLocaleString()} KRW`;
            } else {
                ProfitValueElement.textContent = `${profitValue.toFixed(2).toLocaleString()} KRW`;
            }
            BTCValueElement.textContent = `${BTCValue.toFixed(2).toLocaleString()} KRW`;
            KRWValueElement.textContent = `${KRWValue.toFixed(2).toLocaleString()} KRW`;
        })
        .catch(error => console.error(error));
}

async function fetchBitcoinNews() {
    try {
        const response = await fetch("https://min-api.cryptocompare.com/data/v2/news/?categories=BTC");
        const data = await response.json();

        if (data.Data) {
            return data.Data.slice(0, 3); // 최근 3개 뉴스
        } else {
            console.error("Failed to fetch news:", data);
            return [];
        }
    } catch (error) {
        console.error("Error fetching news:", error);
        return [];
    }
}

function updateNewsTable(articles) {
    const tableBody = document.getElementById("news-table-body");

    // 기존 뉴스 목록 초기화
    tableBody.innerHTML = "";

    let order = 1; // 뉴스 순서 초기화

    articles.forEach((article) => {
        const row = document.createElement("tr");

        // 순서 표시
        const orderCell = document.createElement("td");
        orderCell.classList.add("news-order");
        orderCell.textContent = order;
        row.appendChild(orderCell);

        // 제목과 링크
        const titleCell = document.createElement("td");
        const titleLink = document.createElement("a");
        titleLink.href = article.url;
        titleLink.textContent = article.title;
        titleLink.target = "_blank";
        titleCell.appendChild(titleLink);
        row.appendChild(titleCell);

        tableBody.appendChild(row);
        order++; // 순서 증가
    });
}

// form을 이벤트리스너에 삽입
document.addEventListener("DOMContentLoaded", function () {
    // Attach submit event to all forms
    const forms = document.querySelectorAll("form");
    forms.forEach(form => {
        form.removeEventListener("submit", handleSubmitEvent);
        form.addEventListener("submit", handleSubmitEvent);
    });
});

// url 변경 금지
function handleSubmitEvent(event) {
    event.preventDefault(); // Prevent default form submission
    submitForm(event.target.id); // Call submitForm with the form's ID
}

//자동매매용 AJAX
function submitForm(formId) {
        const form = document.getElementById(formId);
        const formData = new FormData(form);
        const url = form.action;

        fetch(url, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json()) // Expect JSON response
        .then(data => {
            if (data.success) {
                // Update the UI based on the response
                console.log('Form submitted successfully:', data);
            } else {
                console.error('Form submission error:', data.error);
            }
        })
        .catch(error => console.error('Error:', error));
    }

// 자동 트레이드 버튼에 threshold 정보 삽입
function addThresholdLevelToForm(form) {
    let hiddenInput = form.querySelector('input[name="ThresholdLevel"]');
    if (!hiddenInput) {
        hiddenInput = document.createElement('input');
        hiddenInput.type = 'hidden';
        hiddenInput.name = 'ThresholdLevel';
        form.appendChild(hiddenInput);
    }
    hiddenInput.value = document.getElementById('hidden-Threshold-level').value;
}
//form button display 설정
function handleForm1Click() {
    // Show Form 2 and keep Form 3 visible
    document.getElementById("form2").style.display = "block";
    document.getElementById("form3").style.display = "block";
    document.getElementById("form1").style.display = "none"; // Hide Form 1
    return false; // Prevent default form submission
}

function handleForm2Click() {
    // Keep Form 2 and Form 3 visible
    document.getElementById("form2").style.display = "block";
    document.getElementById("form3").style.display = "block";
    return false; // Prevent default form submission
}

function handleForm3Click() {
    // Show Form 1 and keep Form 3 visible
    document.getElementById("form1").style.display = "block";
    document.getElementById("form3").style.display = "block";
    document.getElementById("form2").style.display = "none"; // Hide Form 2
    return false; // Prevent default form submission
}

///////////////////중복 주의
// WebSocket 초기화
const upbitSocket = new WebSocket('wss://api.upbit.com/websocket/v1');

// 최근 체결 데이터 저장 배열
let recentTrades = [];

// 체결 데이터 테이블
const tradeTableBody = document.getElementById('tradeTableBody');

// WebSocket 연결
upbitSocket.onopen = () => {
    console.log('WebSocket Connected');
    // 업비트 WebSocket 구독 메시지 (KRW-BTC 체결 정보)
    const subscribeMessage = [
        { ticket: "test" },
        { type: "trade", codes: ["KRW-BTC"] }
    ];
    upbitSocket.send(JSON.stringify(subscribeMessage));
};

// 메시지 수신
upbitSocket.onmessage = async (event) => {
    try {
        // Blob 데이터를 텍스트로 변환
        const textData = await event.data.text();
        const data = JSON.parse(textData); // JSON으로 변환
        if (data.type === 'trade') {
            // 체결가와 체결량 추가
            const tradePrice = data.trade_price; // 체결가
            const tradeVolume = data.trade_volume; // 체결량

            // 최근 데이터에 추가
            recentTrades.unshift({ price: tradePrice, volume: tradeVolume });
            
            // 최근 10개 데이터 유지
            if (recentTrades.length > 5) {
                recentTrades.pop();
            }

            // 테이블 업데이트
            updateTable();
        }
    } catch (error) {
        console.error('Error parsing WebSocket message:', error);
    }
};

// 테이블 업데이트 함수
function updateTable() {
    // 테이블 내용 초기화
    tradeTableBody.innerHTML = '';

    // 최근 데이터 추가
    recentTrades.forEach((trade) => {
        const row = document.createElement('tr');
        row.className = 'upbit-realtime-tr';

        const priceCell = document.createElement('td');
        priceCell.className = 'upbit-realtime-td';
        priceCell.textContent = `${trade.price.toLocaleString()} KRW`;

        const volumeCell = document.createElement('td');
        volumeCell.className = 'upbit-realtime-td';
        volumeCell.textContent = `${trade.volume.toFixed(4)}`;

        row.appendChild(priceCell);
        row.appendChild(volumeCell);
        tradeTableBody.appendChild(row);
    });
}

// WebSocket 에러 처리
upbitSocket.onerror = (error) => {
    console.error('WebSocket Error:', error);
};

// WebSocket 종료
upbitSocket.onclose = () => {
    console.log('WebSocket Disconnected');
};

// 최근 7일 데이터 저장
const weekData = {
    timestamps: [], // 날짜 데이터
    prices: []      // 가격 데이터
};

// 차트 초기화
let btcWeekChart;
function initializeWeekChart() {
    const ctx = document.getElementById("btcWeekChart").getContext("2d");
    btcWeekChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: weekData.timestamps, // X축 날짜
            datasets: [{
                label: "최근 7일 비트코인 가격",
                data: weekData.prices,   // Y축 가격
                borderColor: "rgba(255, 99, 132, 1)", // 선 색상 (분홍색)
                backgroundColor: "rgba(255, 99, 132, 0.2)", // 배경색 (투명 분홍색)
                tension: 0.4, // 부드러운 곡선
                pointRadius: 4, // 데이터 포인트 크기
                pointHoverRadius: 8, // 커서를 올릴 때 데이터 포인트 크기
                fill: true // 선 아래를 채움
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    enabled: true, // 툴팁 활성화
                    callbacks: {
                        label: function (context) {
                            const value = context.raw; // 해당 데이터 값
                            return `가격: ${value.toLocaleString()} KRW`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: "날짜"
                    },
                    ticks: {
                        maxTicksLimit: 7 // X축에 표시되는 최대 날짜 수
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: "가격 (KRW)"
                    },
                    ticks: {
                        callback: function (value) {
                            return value.toLocaleString() + " KRW"; // Y축 값 포맷
                        }
                    }
                }
            },
            interaction: {
                mode: "nearest", // 가장 가까운 데이터 포인트에 반응
                intersect: false // 선 위에 있을 때도 반응
            }
        }
    });
}

// Upbit API를 통해 최근 7일 데이터 가져오기
async function fetchWeekData() {
    const apiUrl = "/proxy/upbit/candles?market=KRW-BTC&count=7";

    try {
        const response = await fetch(apiUrl);
        const data = await response.json();

        // 데이터 처리
        weekData.timestamps = data.map((item) => item.candle_date_time_kst.split("T")[0]); // 날짜 (YYYY-MM-DD)
        weekData.prices = data.map((item) => item.trade_price); // 종가

        console.log("Fetched Week Data:", weekData);

        // 차트 업데이트
        btcWeekChart.data.labels = weekData.timestamps.reverse(); // 날짜 역순으로 변경
        btcWeekChart.data.datasets[0].data = weekData.prices.reverse(); // 가격 역순으로 변경
        btcWeekChart.update();
    } catch (error) {
        console.error("Error fetching week data:", error);
    }
}

// 차트 초기화 및 데이터 가져오기
initializeWeekChart();
fetchWeekData();

// 최근 한달 차트 만들기 

// 최근 한 달 데이터 저장
const monthData = {
    timestamps: [], // 날짜 데이터
    prices: []      // 가격 데이터
};

// 차트 초기화
let btcMonthChart;
function initializeMonthChart() {
    const ctx = document.getElementById("btcMonthChart").getContext("2d");
    btcMonthChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: monthData.timestamps, // X축 날짜
            datasets: [{
                label: "최근 한 달 비트코인 가격",
                data: monthData.prices,   // Y축 가격
                borderColor: "rgba(75, 192, 192, 1)", // 선 색상
                backgroundColor: "rgba(75, 192, 192, 0.2)", // 배경 색상
                tension: 0.4, // 부드러운 곡선
                pointRadius: 3, // 데이터 포인트 크기
                pointHoverRadius: 6, // 커서를 올릴 때 데이터 포인트 크기
                fill: true // 선 아래를 채움
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    enabled: true, // 툴팁 활성화
                    callbacks: {
                        label: function (context) {
                            const value = context.raw; // 해당 데이터 값
                            return `가격: ${value.toLocaleString()} KRW`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: "날짜"
                    },
                    ticks: {
                        maxTicksLimit: 10 // X축에 표시되는 최대 날짜 수
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: "가격 (KRW)"
                    },
                    ticks: {
                        callback: function (value) {
                            return value.toLocaleString() + " KRW"; // Y축 값 포맷
                        }
                    }
                }
            },
            interaction: {
                mode: "nearest", // 가장 가까운 데이터 포인트에 반응
                intersect: false // 선 위에 있을 때도 반응
            }
        }
    });
}

// Upbit API를 통해 최근 한 달 데이터 가져오기
async function fetchMonthData() {
    const apiUrl = "/proxy/upbit/candles?market=KRW-BTC&count=30";

    try {
        const response = await fetch(apiUrl);
        const data = await response.json();

        // 데이터 처리
        monthData.timestamps = data.map((item) => item.candle_date_time_kst.split("T")[0]); // 날짜 (YYYY-MM-DD)
        monthData.prices = data.map((item) => item.trade_price); // 종가

        console.log("Fetched Month Data:", monthData);

        // 차트 업데이트
        btcMonthChart.data.labels = monthData.timestamps.reverse(); // 날짜 역순으로 변경
        btcMonthChart.data.datasets[0].data = monthData.prices.reverse(); // 가격 역순으로 변경
        btcMonthChart.update();
    } catch (error) {
        console.error("Error fetching month data:", error);
    }
}

// 차트 초기화 및 데이터 가져오기
initializeMonthChart();
fetchMonthData();

// 3개월 데이터 저장
const threeMonthData = {
    timestamps: [], // 날짜 데이터
    prices: []      // 가격 데이터
};

// 6개월 데이터 저장
const sixMonthData = {
    timestamps: [], // 날짜 데이터
    prices: []      // 가격 데이터
};

// 차트 초기화 변수
let btcThreeMonthChart;
let btcSixMonthChart;

// 3개월 차트 초기화
function initializeThreeMonthChart() {
    const ctx = document.getElementById("btcThreeMonthChart").getContext("2d");
    btcThreeMonthChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: threeMonthData.timestamps, // X축 날짜
            datasets: [{
                label: "최근 3개월 비트코인 가격",
                data: threeMonthData.prices,   // Y축 가격
                borderColor: "rgba(255, 159, 64, 1)", // 선 색상 (오렌지색)
                backgroundColor: "rgba(255, 159, 64, 0.2)", // 배경색 (투명 오렌지색)
                tension: 0.4, // 부드러운 곡선
                pointRadius: 3,
                pointHoverRadius: 6,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    enabled: true,
                    callbacks: {
                        label: function (context) {
                            const value = context.raw;
                            return `가격: ${value.toLocaleString()} KRW`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: "날짜"
                    },
                    ticks: {
                        maxTicksLimit: 15
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: "가격 (KRW)"
                    },
                    ticks: {
                        callback: function (value) {
                            return value.toLocaleString() + " KRW";
                        }
                    }
                }
            },
            interaction: {
                mode: "nearest",
                intersect: false
            }
        }
    });
}

// 6개월 차트 초기화
function initializeSixMonthChart() {
    const ctx = document.getElementById("btcSixMonthChart").getContext("2d");
    btcSixMonthChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: sixMonthData.timestamps, // X축 날짜
            datasets: [{
                label: "최근 6개월 비트코인 가격",
                data: sixMonthData.prices,   // Y축 가격
                borderColor: "rgba(54, 162, 235, 1)", // 선 색상 (파란색)
                backgroundColor: "rgba(54, 162, 235, 0.2)", // 배경색 (투명 파란색)
                tension: 0.4,
                pointRadius: 3,
                pointHoverRadius: 6,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    enabled: true,
                    callbacks: {
                        label: function (context) {
                            const value = context.raw;
                            return `가격: ${value.toLocaleString()} KRW`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: "날짜"
                    },
                    ticks: {
                        maxTicksLimit: 20
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: "가격 (KRW)"
                    },
                    ticks: {
                        callback: function (value) {
                            return value.toLocaleString() + " KRW";
                        }
                    }
                }
            },
            interaction: {
                mode: "nearest",
                intersect: false
            }
        }
    });
}

// 3개월 데이터 가져오기
async function fetchThreeMonthData() {
    const apiUrl = "/proxy/upbit/candles?market=KRW-BTC&count=91"; // 3개월 데이터 (90일)

    try {
        const response = await fetch(apiUrl);
        const data = await response.json();

        // 데이터 처리
        threeMonthData.timestamps = data.map((item) => item.candle_date_time_kst.split("T")[0]); // 날짜
        threeMonthData.prices = data.map((item) => item.trade_price); // 종가

        console.log("Fetched Three-Month Data:", threeMonthData);

        // 차트 업데이트
        btcThreeMonthChart.data.labels = threeMonthData.timestamps.reverse();
        btcThreeMonthChart.data.datasets[0].data = threeMonthData.prices.reverse();
        btcThreeMonthChart.update();
    } catch (error) {
        console.error("Error fetching three-month data:", error);
    }
}

// 6개월 데이터 가져오기
async function fetchSixMonthData() {
    const apiUrl = "/proxy/upbit/candles?market=KRW-BTC&count=183"; // 6개월 데이터 (180일)

    try {
        const response = await fetch(apiUrl);
        const data = await response.json();

        // 데이터 처리
        sixMonthData.timestamps = data.map((item) => item.candle_date_time_kst.split("T")[0]); // 날짜
        sixMonthData.prices = data.map((item) => item.trade_price); // 종가

        console.log("Fetched Six-Month Data:", sixMonthData);

        // 차트 업데이트
        btcSixMonthChart.data.labels = sixMonthData.timestamps.reverse();
        btcSixMonthChart.data.datasets[0].data = sixMonthData.prices.reverse();
        btcSixMonthChart.update();
    } catch (error) {
        console.error("Error fetching six-month data:", error);
    }
}

// 차트 초기화 및 데이터 가져오기
initializeThreeMonthChart();
initializeSixMonthChart();
fetchThreeMonthData();
fetchSixMonthData();


// --------------------

function showChart(chartId) {
    // 모든 차트를 숨김
    const chartContainers = document.querySelectorAll('.chart-container');
    chartContainers.forEach(container => container.classList.add('hidden'));

    // 클릭된 차트 컨테이너만 표시
    const selectedChartContainer = document.getElementById(`${chartId}-container`);
    if (selectedChartContainer) {
        selectedChartContainer.classList.remove('hidden');
    }

    // 버튼 활성화 상태 설정
    const buttons = document.querySelectorAll('.tab-button');
    buttons.forEach(button => button.classList.remove('active'));

    // 현재 버튼 활성화
    event.target.classList.add('active');
}
