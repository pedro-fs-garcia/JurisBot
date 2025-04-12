document.addEventListener('DOMContentLoaded', () => {
    // Chat functionality
    const chatMessages = document.getElementById('chat-messages');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const typingIndicator = document.getElementById('typing-indicator');

    // Função para adicionar mensagem ao chat
    function addMessage(content, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.textContent = content;
        
        messageDiv.appendChild(messageContent);
        chatMessages.appendChild(messageDiv);
        
        // Scroll para a última mensagem
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Função para enviar mensagem para o backend
    async function sendMessage(message) {
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message }),
            });

            if (!response.ok) {
                throw new Error('Erro na resposta do servidor');
            }

            const data = await response.json();
            return data.response;
        } catch (error) {
            console.error('Erro:', error);
            return 'Desculpe, ocorreu um erro ao processar sua mensagem.';
        }
    }

    // Função para lidar com o envio de mensagem
    async function handleSendMessage() {
        const message = messageInput.value.trim();
        if (!message) return;

        // Adiciona mensagem do usuário
        addMessage(message, true);
        messageInput.value = '';

        // Mostra indicador de digitação
        typingIndicator.classList.remove('d-none');
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Envia mensagem para o backend e recebe resposta
        const response = await sendMessage(message);

        // Esconde indicador de digitação
        typingIndicator.classList.add('d-none');

        // Adiciona resposta do bot
        addMessage(response);
    }

    // Event listeners para o chat
    sendButton.addEventListener('click', handleSendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleSendMessage();
        }
    });

    // Existing search functionality
    const searchForm = document.getElementById('searchForm');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const iaResults = document.getElementById('ia-results-content');
    const googleResults = document.getElementById('google-results');
    const dizerodireitoResults = document.getElementById('dizerodireito-results');
    const jusbrasilResults = document.getElementById('jusbrasil-results');

    searchForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const query = document.getElementById('query').value.trim();
        
        if (!query) return;

        // Show loading
        loading.classList.remove('d-none');
        results.classList.add('d-none');

        try {
            // TODO: Implement search functionality
            // const response = await fetch('/search', {
            //     method: 'POST',
            //     headers: {
            //         'Content-Type': 'application/json',
            //     },
            //     body: JSON.stringify({ query }),
            // });

            // if (!response.ok) {
            //     throw new Error('Erro na busca');
            // }

            // const data = await response.json();
            // displayResults(data);

        } catch (error) {
            console.error('Erro:', error);
            alert('Ocorreu um erro durante a busca. Por favor, tente novamente.');
        } finally {
            loading.classList.add('d-none');
            results.classList.remove('d-none');
        }
    });

    function displayResults(data) {
        // TODO: Implement results display
        // Clear previous results
        iaResults.innerHTML = '';
        googleResults.innerHTML = '';
        dizerodireitoResults.innerHTML = '';
        jusbrasilResults.innerHTML = '';

        // Display new results
        // ...
    }
}); 