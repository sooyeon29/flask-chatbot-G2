// HTML 요소 가져오기
const userInfoForm = document.getElementById('user-info-form');
const userInfoContainer = document.getElementById('user-info-container');
const chatContainer = document.getElementById('chat-container');
const chatOutput = document.getElementById('chat-output');
const textInputForm = document.getElementById('text-input-form');
const textInput = document.getElementById('text-input');

let timer;

// 채팅 화면을 아래로 스크롤하는 함수
function scrollToBottom() {
    chatOutput.scrollTop = chatOutput.scrollHeight;
}

// 페이지 로드 시 초기화
// window.onload = () => {
//     userInfoContainer.style.display = 'block';
//     chatContainer.style.display = 'none';
// };
// 새로운 사용자 인식 위한 새로고침 처리
window.onload = async () => {
    await fetch('/reset-session', { method: 'POST' }); // 새 세션 요청
    userInfoContainer.style.display = 'block';
    chatContainer.style.display = 'none';
};


// 사용자 정보 폼 제출 처리
userInfoForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const userInfo = {
        name: document.getElementById('name').value,
        dob: document.getElementById('dob').value,
        gender: document.getElementById('gender').value
    };

    try {
        await fetch('/user-info', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userInfo)
        });
    } catch (err) {
        console.error('사용자 정보 저장 중 오류:', err);
        return;
    }

    userInfoContainer.style.display = 'none';
    chatContainer.style.display = 'block';
    document.getElementById('chat-header').style.display = 'flex'; // 헤더 보이기
    
    addBotMessage(`안녕 ${userInfo.name}~! 나는 사랑세포야. 오늘 사랑과 관련된 고민에 대해 이야기 나눠보자! 
    내가 고민해결 다 해줄게~! 
    사랑 관련해서는 내가 전문가라고!!`);

    scrollToBottom(); // 화면 하단으로 스크롤
    startTimers();
});

// 채팅 폼 제출 처리
// 채팅 폼 제출 처리
textInputForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    sendMessage();
});

// 엔터 키 입력 감지
textInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { // Shift + Enter는 줄바꿈, Enter는 전송
        e.preventDefault(); // 기본 Enter 동작 방지
        sendMessage(); // 메시지 전송
    }
});

// 메시지 전송 함수
function sendMessage() {
    const userInput = textInput.value.trim();
    if (!userInput) return;

    addUserMessage(userInput);
    textInput.value = ''; // 입력창 초기화
    scrollToBottom();

    // 서버로 메시지 전송
    fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_input: userInput })
    })
    .then(response => response.json())
    .then(data => {
        addBotMessage(data.reply);
        scrollToBottom();
    })
    .catch(err => {
        console.error('채팅 중 오류:', err);
    });
}

// 사용자 메시지를 채팅에 추가
function addUserMessage(message) {
    const userMessage = document.createElement('div');
    userMessage.className = 'user-message';
    userMessage.textContent = message;
    chatOutput.appendChild(userMessage);
}

// 봇 메시지를 채팅에 추가 (프로필 사진 포함)
function addBotMessage(message) {
    const botMessageContainer = document.createElement('div');
    botMessageContainer.className = 'bot-message-container';

    const botProfilePic = document.createElement('img');
    botProfilePic.src = 'love_cell_profile.jpg';
    botProfilePic.alt = '사랑세포';
    botProfilePic.className = 'profile-pic';

    const botMessage = document.createElement('div');
    botMessage.className = 'bot-message';
    botMessage.textContent = message;

    botMessageContainer.appendChild(botProfilePic);
    botMessageContainer.appendChild(botMessage);
    chatOutput.appendChild(botMessageContainer);
    scrollToBottom();
}

// 채팅 화면을 아래로 스크롤하는 함수
function scrollToBottom() {
    chatOutput.scrollTop = chatOutput.scrollHeight;
}

// textInputForm.addEventListener('submit', async (e) => {
//     e.preventDefault();
//     const userInput = textInput.value.trim();
//     if (!userInput) return;

//     addUserMessage(userInput);
//     textInput.value = '';
//     scrollToBottom();

//     try {
//         const response = await fetch('/chat', {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({ user_input: userInput })
//         });
//         const data = await response.json();
//         addBotMessage(data.reply);
//     } catch (err) {
//         console.error('채팅 중 오류:', err);
//     }

//     scrollToBottom();
// });

// // 사용자 메시지를 채팅에 추가
// function addUserMessage(message) {
//     const userMessage = document.createElement('div');
//     userMessage.className = 'user-message';
//     userMessage.textContent = message;
//     chatOutput.appendChild(userMessage);
// }

// // 봇 메시지를 채팅에 추가 (프로필 사진 포함)
// function addBotMessage(message) {
//     const botMessageContainer = document.createElement('div');
//     botMessageContainer.className = 'bot-message-container';

//     const botProfilePic = document.createElement('img');
//     botProfilePic.src = 'love_cell_profile.jpg';
//     botProfilePic.alt = '사랑세포';
//     botProfilePic.className = 'profile-pic';

//     const botMessage = document.createElement('div');
//     botMessage.className = 'bot-message';
//     botMessage.textContent = message;

//     botMessageContainer.appendChild(botProfilePic);
//     botMessageContainer.appendChild(botMessage);
//     chatOutput.appendChild(botMessageContainer);
// }

// 10분 타이머 시작
// function startTimer() {
//     timer = setTimeout(async () => {
//         addBotMessage('벌써 오늘 대화할 수 있는 시간이 모두 끝났네! 너무 즐거웠어! 오늘 나와의 대화가 너의 연애 관련 스트레스를 푸는데 도움이되었기를 바래!');
//         await endChatSession();
//     }, 10 * 60 * 1000);
// }

let startTime, endTime, timer5Min, timer15Min;

function startTimers() {
    startTime = new Date();

    // 5분 타이머: 완료하기 버튼 표시
    timer5Min = setTimeout(() => {
        const finishButton = document.createElement('button');
        finishButton.textContent = '완료하기';
        finishButton.className = 'finish-button'; // 완료하기 버튼에 클래스 적용
        finishButton.style.marginTop = '10px';

        // 완료 버튼 클릭 시 동작 정의
        finishButton.onclick = async () => {
            try {
                // 데이터베이스에 완료 상태 저장
                await fetch('/complete-session', { method: 'POST' });

                // 다음 페이지로 전환
                chatContainer.style.display = 'none';
                document.getElementById('final-page').style.display = 'block';
            } catch (err) {
                console.error('완료 상태 저장 중 오류:', err);
            }
        };

        chatContainer.appendChild(finishButton);
    }, 5 * 60 * 1000);

    // 15분 타이머: 자동 종료 처리
    timer15Min = setTimeout(() => {
        addBotMessage('대화 시간이 모두 종료되어! 오늘 이야기를 나눠줘서 고마워, 아쉽지만 다음에 더 대화를 이어나가자!');
        textInputForm.style.display = 'none';

        // 완료하기 버튼만 남기기
        const finishButton = document.querySelector('.finish-button');
        if (finishButton) finishButton.style.display = 'block';

        // 10초 후 자동 이동
        setTimeout(async () => {
            try {
                // 자동 완료 상태를 서버에 저장
                await fetch('/complete-session', { method: 'POST' });

                // 마지막 페이지로 전환
                chatContainer.style.display = 'none';
                document.getElementById('final-page').style.display = 'block';
            } catch (err) {
                console.error('자동 완료 처리 중 오류:', err);
            }
        }, 10000); // 10초 대기
    }, 15 * 60 * 1000);
}



// 채팅 세션 종료 및 서버에 알림
async function endChatSession() {
    try {
        const response = await fetch('/end-chat', { method: 'POST' });
        const data = await response.json();
        addBotMessage(data.message);
        textInputForm.style.display = 'none';
    } catch (err) {
        console.error('채팅 종료 중 오류:', err);
    }
}

// 실시간 데이터 미리보기
async function fetchData() {
    try {
        const response = await fetch('/view-data');
        const data = await response.text();
        // console.log('Fetched Data:', data); // 데이터를 콘솔에 출력
    } catch (err) {
        console.error('데이터 가져오기 오류:', err);
    }
}



// 5초마다 데이터 갱신
setInterval(fetchData, 10000);
