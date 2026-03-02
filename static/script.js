// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('hu-HU', { year: 'numeric', month: '2-digit', day: '2-digit' });
}

function formatDayName(dateString) {
    const date = new Date(dateString);
    const days = ['vasárnap', 'hétfő', 'kedd', 'szerda', 'csütörtök', 'péntek', 'szombat'];
    return days[date.getDay()];
}

// Chat functions
async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (!message) return;

    addChatMessage(message, 'user');
    input.value = '';

    const loadingId = 'loading-' + Date.now();
    addChatMessage('Gondolkodás...', 'ai loading', loadingId);

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });
        
        const data = await response.json();
        
        const loadingEl = document.getElementById(loadingId);
        if (loadingEl) loadingEl.remove();
        
        addChatMessage(data.response, 'ai');
        
        const messagesDiv = document.getElementById('chatMessages');
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    } catch (error) {
        console.error('Chat error:', error);
        const loadingEl = document.getElementById(loadingId);
        if (loadingEl) {
            loadingEl.textContent = '❌ Hiba történt az AI-val való kommunikáció során.';
            loadingEl.classList.remove('loading');
        }
    }
}

function handleChatKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendChatMessage();
    }
}

function addChatMessage(text, type, id = null) {
    const messagesDiv = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${type}-message`;
    if (id) messageDiv.id = id;
    
    messageDiv.textContent = text;
    messageDiv.innerHTML = messageDiv.innerHTML.replace(/\n/g, '<br>');

    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function toggleChat() {
    const chatContainer = document.querySelector('.chat-container');
    const toggleIcon = document.getElementById('chatToggleIcon');

    if (!chatContainer || !toggleIcon) return;

    chatContainer.classList.toggle('chat-collapsed');
    toggleIcon.textContent = chatContainer.classList.contains('chat-collapsed') ? '▶' : '▼';
}

// Settings functions
async function saveSettings() {
    const calorieGoal = document.getElementById('calorieGoal').value;
    const exclusions = document.getElementById('exclusions').value;
    const preferences = document.getElementById('preferences').value;
    
    try {
        const response = await fetch('/api/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                calorie_goal: calorieGoal,
                exclusions: exclusions,
                preferences: preferences
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('✅ Beállítások mentve!');
        } else {
            alert('❌ Hiba történt a mentés során!');
        }
    } catch (error) {
        console.error('Settings error:', error);
        alert('❌ Hiba történt!');
    }
}

function toggleSettingsOverlay() {
    document.getElementById('settingsOverlay').style.display = 'flex';
}

function closeSettingsOverlay() {
    document.getElementById('settingsOverlay').style.display = 'none';
}

// Google Keep integration
async function connectGoogleKeep() {
    if (!confirm('Szeretnéd csatlakoztatni a Google fiókodat a Google Keep szolgáltatáshoz?')) {
        return;
    }
    
    try {
        const response = await fetch('/api/google/connect');
        if (response.ok) {
            alert('✅ Google fiók csatlakoztatva! A bevásárlólista mostantól automatikusan szinkronizálódik.');
        } else {
            alert('❌ Hiba történt a csatlakoztatás során.');
        }
    } catch (error) {
        console.error('Google Keep error:', error);
        alert('❌ Hiba történt!');
    }
}

// Meal plan functions
async function generateMealPlan(date) {
    const mealsList = document.getElementById(`meals-${date}`);
    mealsList.innerHTML = '<div class="loading">🤖 AI étrend generálása... (20-40 másodperc)</div>';
    
    const calorieGoal = document.getElementById('calorieGoal').value || 2000;
    const exclusions = document.getElementById('exclusions').value || 'nincs';
    const preferences = document.getElementById('preferences').value || 'nincs megadva';

    const prompt = `Készíts egy TELJES napi étrendet (${formatDayName(date)}, ${formatDate(date)}) ${calorieGoal} kalóriára.
Kizárások: ${exclusions}
Preferenciák: ${preferences}
Az étrend tartalmazza MIND az 5 étkezést:
Reggeli (kalória)
Tízórai (kalória)
Ebéd (kalória)
Uzsonna (kalória)
Vacsora (kalória)
Minden étkezéshez írj egy RÖVID, gyakorlatias receptet (max 3 mondat). NE használj JSON-t, csak egyszerű szöveget formázva:
REGGELI: [étel neve] ([kalória] kcal)
[recept]
TÍZÓRAI: [étel neve] ([kalória] kcal)
[recept]
EBÉD: [étel neve] ([kalória] kcal)
[recept]
UZSONNA: [étel neve] ([kalória] kcal)
[recept]
VACSORA: [étel neve] ([kalória] kcal)
[recept]

További elvárások:
- Ne legyenek egymást követő napokon ugyanazok az ételek.
- Legyen változatosabb reggeli/tízórai/uzsonna, ne mindig ugyanaz a minta.
- Legyen praktikus: ebédeknél és vacsoráknál lehet okos előkészítés, hogy ne kelljen sokat főzni.
- Ha valami ismétlődik, az tudatosan legyen tervezve (pl. másnapi ebéd maradékból).`;
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: prompt })
        });
        
        const data = await response.json();
        
        const meals = parseMealPlanResponse(data.response);
        
        await fetch(`/api/meals/${date}`, {
            method: 'DELETE'
        });
        
        for (const meal of meals) {
            await fetch('/api/meals', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    date: date,
                    meal_type: meal.type,
                    name: meal.name,
                    calories: meal.calories,
                    recipe: meal.recipe
                })
            });
        }
        
        location.reload();
        
    } catch (error) {
        console.error('Meal plan error:', error);
        mealsList.innerHTML = `<div class="error">❌ Hiba: ${error.message || 'Ismeretlen hiba'}</div>`;
    }
}

function parseMealPlanResponse(text) {
    const meals = [];
    const lines = text.split('\n').filter(line => line.trim());
    let currentMeal = null;
    const mealTypes = {
        'reggeli': 'reggeli',
        'tízórai': 'tízórai',
        'tizorai': 'tízórai',
        'ebéd': 'ebéd',
        'ebed': 'ebéd',
        'uzsonna': 'uzsonna',
        'vacsora': 'vacsora'
    };

    for (let line of lines) {
        line = line.trim().toLowerCase();
        
        for (const [key, type] of Object.entries(mealTypes)) {
            if (line.includes(key)) {
                if (currentMeal && currentMeal.name) {
                    meals.push(currentMeal);
                }
                
                currentMeal = {
                    type: type,
                    name: '',
                    calories: 0,
                    recipe: ''
                };
                
                const calMatch = line.match(/(\d+)\s*kcal/i);
                if (calMatch) {
                    currentMeal.calories = parseInt(calMatch[1]) || 300;
                }
                
                const nameMatch = line.match(/(?:reggeli|tízórai|tizorai|ebéd|ebed|uzsonna|vacsora):\s*([^(\n]+)/i);
                if (nameMatch) {
                    currentMeal.name = nameMatch[1].trim().replace(/\*\*/g, '').trim();
                }
                break;
            }
        }
        
        if (currentMeal && currentMeal.name && 
            !line.includes('reggeli') && !line.includes('tízórai') && 
            !line.includes('tizorai') && !line.includes('ebéd') && 
            !line.includes('ebed') && !line.includes('uzsonna') && 
            !line.includes('vacsora')) {
            if (!currentMeal.recipe) {
                currentMeal.recipe = line;
            } else {
                currentMeal.recipe += '\n' + line;
            }
        }
    }

    if (currentMeal && currentMeal.name) {
        meals.push(currentMeal);
    }

    if (meals.length === 0) {
        return [
            {type: 'reggeli', name: 'Teljes kiőrlésű kenyér tojással', calories: 400, recipe: text},
            {type: 'tízórai', name: 'Gyümölcs', calories: 150, recipe: '1 alma vagy banán'},
            {type: 'ebéd', name: 'Csirke zöldségekkel', calories: 600, recipe: 'Grillezett csirkemell zöldségekkel'},
            {type: 'uzsonna', name: 'Joghurt', calories: 150, recipe: 'Görög joghurt gyümölccsel'},
            {type: 'vacsora', name: 'Hal zöldséges salátával', calories: 500, recipe: 'Sült lazac zöldséges salátával'}
        ];
    }

    return meals;
}

async function clearDay(date) {
    if (!confirm(`Biztosan törölni szeretnéd az összes ételt ezen a napon (${formatDate(date)})?`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/meals/${date}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            document.getElementById(`meals-${date}`).innerHTML = '<div class="no-meals">Még nincs étel</div>';
            alert('✅ Ételek törölve!');
        }
    } catch (error) {
        console.error('Delete error:', error);
        alert('❌ Hiba történt a törlés során!');
    }
}

function formatHungarianDayName(dateObj) {
    const dayName = dateObj.toLocaleDateString('hu-HU', { weekday: 'long' });
    return dayName.charAt(0).toUpperCase() + dayName.slice(1);
}

function formatHungarianDateNumber(dateObj) {
    const year = dateObj.getFullYear();
    const month = String(dateObj.getMonth() + 1).padStart(2, '0');
    const day = String(dateObj.getDate()).padStart(2, '0');
    return `${year}. ${month}. ${day}.`;
}

function getAddedDaysFromStorage() {
    try {
        const raw = localStorage.getItem('addedMealPlannerDays');
        return raw ? JSON.parse(raw) : [];
    } catch {
        return [];
    }
}

function saveAddedDaysToStorage(days) {
    localStorage.setItem('addedMealPlannerDays', JSON.stringify(days));
}

function renderExtraDayCard(isoDate) {
    if (document.getElementById(`day-${isoDate}`)) {
        return;
    }

    const calendarGrid = document.querySelector('.calendar-grid');
    const addDayCard = document.querySelector('.add-day-card');
    if (!calendarGrid || !addDayCard) return;

    const dateObj = new Date(`${isoDate}T12:00:00`);
    const dayName = formatHungarianDayName(dateObj);
    const dayNumber = formatHungarianDateNumber(dateObj);

    const card = document.createElement('div');
    card.className = 'calendar-day';
    card.id = `day-${isoDate}`;
    card.innerHTML = `
        <div class="day-header">
            <div class="day-name">${dayName}</div>
            <div class="day-date">${dayNumber}</div>
        </div>

        <div class="meals-list" id="meals-${isoDate}">
            <div class="no-meals">Még nincs étel</div>
        </div>

        <div class="day-actions">
            <button class="btn btn-small btn-generate" onclick="generateMealPlan('${isoDate}')">🤖 AI Étrend</button>
            <button class="btn btn-small btn-danger" onclick="clearDay('${isoDate}')">🗑️ Törlés</button>
        </div>
    `;

    calendarGrid.insertBefore(card, addDayCard);
}

function addNewDayCard() {
    const dayCards = Array.from(document.querySelectorAll('.calendar-day[id^="day-"]'));
    if (dayCards.length === 0) return;

    const isoDates = dayCards
        .map(card => card.id.replace('day-', ''))
        .filter(Boolean)
        .sort();

    const latestIsoDate = isoDates[isoDates.length - 1];
    const nextDate = new Date(`${latestIsoDate}T12:00:00`);
    nextDate.setDate(nextDate.getDate() + 1);

    const nextIsoDate = nextDate.toISOString().split('T')[0];
    renderExtraDayCard(nextIsoDate);

    const storedDays = getAddedDaysFromStorage();
    if (!storedDays.includes(nextIsoDate)) {
        storedDays.push(nextIsoDate);
        saveAddedDaysToStorage(storedDays);
    }
}

function restoreAddedDayCards() {
    const storedDays = getAddedDaysFromStorage();
    storedDays.forEach(isoDate => renderExtraDayCard(isoDate));
}

// Étel Módosítás
let currentModifyMealId = null;

function modifyMeal(mealId, mealName) {
    currentModifyMealId = mealId;
    document.getElementById('modifyMealName').textContent = mealName;
    document.getElementById('modifyMealPopup').style.display = 'flex';
}

function closeModifyMealPopup() {
    document.getElementById('modifyMealPopup').style.display = 'none';
    document.getElementById('modifyMealLoading').style.display = 'none';
    document.getElementById('modifyMealApplyBtn').disabled = false;
    currentModifyMealId = null;
}

async function applyMealModification() {
    const modification = document.getElementById('mealModification').value.trim();
    const loadingEl = document.getElementById('modifyMealLoading');
    const applyButton = document.getElementById('modifyMealApplyBtn');
    
    if (!modification) {
        alert('❌ Kérlek add meg, mit szeretnél módosítani!');
        return;
    }

    loadingEl.style.display = 'block';
    applyButton.disabled = true;
    
    try {
        const response = await fetch(`/api/meal/${currentModifyMealId}/modify`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                modification: modification
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            closeModifyMealPopup();
            alert('✅ Étel sikeresen módosítva!');
            location.reload();
        } else {
            alert('❌ Hiba történt a módosítás során!');
        }
    } catch (error) {
        console.error('Modify meal error:', error);
        alert('❌ Hiba történt!');
    } finally {
        loadingEl.style.display = 'none';
        applyButton.disabled = false;
    }
}

// Recipe popup
function showRecipe(name, recipe, calories) {
    const popup = document.getElementById('recipePopup');
    const title = document.getElementById('recipeTitle');
    const content = document.getElementById('recipeContent');
    
    title.textContent = `${name} (${calories} kcal)`;
    
    content.textContent = recipe;
    content.innerHTML = content.innerHTML.replace(/\n/g, '<br>');
    
    popup.style.display = 'flex';
}

function closeRecipePopup() {
    document.getElementById('recipePopup').style.display = 'none';
}

// Logout
function logout() {
    window.location.href = '/logout';
}

// Load chat history on page load
window.addEventListener('DOMContentLoaded', async () => {
    restoreAddedDayCards();

    try {
        const response = await fetch('/api/chat/history');
        const history = await response.json();
        
        const messagesDiv = document.getElementById('chatMessages');
        history.reverse().forEach(msg => {
            addChatMessage(msg.message, 'user');
            addChatMessage(msg.response, 'ai');
        });
    } catch (error) {
        console.error('Chat history load error:', error);
    }
});

// Close popup on outside click
window.addEventListener('click', (e) => {
    const recipePopup = document.getElementById('recipePopup');
    const modifyMealPopup = document.getElementById('modifyMealPopup');
    const settingsOverlay = document.getElementById('settingsOverlay');
    
    if (e.target === recipePopup) closeRecipePopup();
    if (e.target === modifyMealPopup) closeModifyMealPopup();
    if (e.target === settingsOverlay) closeSettingsOverlay();
});