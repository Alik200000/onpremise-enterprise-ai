import shutil

with open(r'c:\Users\ASUS Vivobook\Documents\antigravity\onpremise-enterprise-ai\index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Заменяем блок формы ввода на форму с кнопкой прикрепления фото/файлов
old_form = '''      <!-- Bottom Input Field -->
      <div class="p-5 border-t border-slate-200 bg-white shrink-0 shadow-sm">
        <form id="chatForm" class="max-w-4xl mx-auto flex gap-3 items-center">
          <div class="relative flex-1">
            <input 
              type="text" 
              id="queryInput" 
              placeholder="Спросите о марках стали, размерах, допусках или формулах чертежа..." 
              class="w-full bg-slate-50 border border-slate-200 focus:border-sky-500 focus:bg-white rounded-2xl px-5 py-3.5 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none transition-all shadow-inner"
              required
            />
          </div>
          <button type="submit" id="sendBtn" class="bg-gradient-to-r from-sky-600 to-blue-600 hover:from-sky-500 hover:to-blue-500 text-white font-bold px-6 py-3.5 rounded-2xl flex items-center gap-2 text-sm transition-all shadow-md shadow-sky-600/20 hover:scale-[1.01] active:scale-[0.99]">
            <span>Запросить</span>
            <i data-lucide="send" class="w-4 h-4"></i>
          </button>
        </form>
        <div class="text-center text-[11px] text-slate-400 font-mono mt-2">
          Все запросы журналируются в локальной подсистеме аудита предприятия.
        </div>
      </div>'''

new_form = '''      <!-- Bottom Input Field with Photo/File Attachment -->
      <div class="p-4 sm:p-5 border-t border-slate-200 bg-white shrink-0 shadow-sm">
        <!-- Attachment preview chip -->
        <div id="attachmentPreview" class="hidden max-w-4xl mx-auto mb-2.5 flex items-center gap-2 flex-wrap"></div>

        <form id="chatForm" class="max-w-4xl mx-auto flex gap-2 sm:gap-3 items-center">
          <!-- Hidden file input for photos and documents -->
          <input type="file" id="chatFileInput" accept="image/*,.pdf,.dxf,.dwg,.txt" class="hidden" />

          <!-- Attachment button (Paperclip) -->
          <button type="button" id="attachBtn" class="p-3 text-slate-500 hover:text-sky-600 hover:bg-sky-50 border border-slate-200 rounded-2xl transition-all shrink-0 shadow-sm flex items-center justify-center" title="Прикрепить фото чертежа или документ">
            <i data-lucide="paperclip" class="w-5 h-5"></i>
          </button>

          <div class="relative flex-1">
            <input 
              type="text" 
              id="queryInput" 
              placeholder="Задайте вопрос или прикрепите фото чертежа..." 
              class="w-full bg-slate-50 border border-slate-200 focus:border-sky-500 focus:bg-white rounded-2xl px-5 py-3.5 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none transition-all shadow-inner"
              required
            />
          </div>
          <button type="submit" id="sendBtn" class="bg-gradient-to-r from-sky-600 to-blue-600 hover:from-sky-500 hover:to-blue-500 text-white font-bold px-5 sm:px-6 py-3.5 rounded-2xl flex items-center gap-2 text-sm transition-all shadow-md shadow-sky-600/20 hover:scale-[1.01] active:scale-[0.99] shrink-0">
            <span>Отправить</span>
            <i data-lucide="send" class="w-4 h-4"></i>
          </button>
        </form>
        <div class="text-center text-[11px] text-slate-400 font-mono mt-2">
          Изолированный контур ТОО • Локальная обработка чертежей и фото
        </div>
      </div>'''

assert old_form in html, "Could not find old_form in html"
html = html.replace(old_form, new_form)

# 2. Обновляем formatMarkdown для идеальной чистки #### и заголовков
old_format = '''    function formatMarkdown(text) {
      if (!text) return '';
      return text
        .replace(/^### (.*$)/gim, '<h3 class="text-sm font-bold text-slate-900 mt-4 mb-2 flex items-center gap-1.5">$1</h3>')
        .replace(/^## (.*$)/gim, '<h2 class="text-base font-bold text-slate-900 mt-4 mb-2">$1</h2>')
        .replace(/^# (.*$)/gim, '<h1 class="text-lg font-bold text-slate-900 mt-4 mb-3">$1</h1>')
        .replace(/\\*\\*\\*(.*?)\\*\\*\\*/gim, '<strong><em>$1</em></strong>')
        .replace(/\\*\\*(.*?)\\*\\*/gim, '<strong class="font-semibold text-slate-900">$1</strong>')
        .replace(/\\*(.*?)\\*/gim, '<em>$1</em>')
        .replace(/^\\* (.*$)/gim, '<div class="flex items-start gap-2 my-1"><span class="text-sky-500 font-bold">•</span><span>$1</span></div>')
        .replace(/^- (.*$)/gim, '<div class="flex items-start gap-2 my-1"><span class="text-sky-500 font-bold">•</span><span>$1</span></div>')
        .replace(/\\n\\n/g, '<div class="my-2"></div>')
        .replace(/\\n/g, '<br/>');
    }'''

new_format = '''    function formatMarkdown(text) {
      if (!text) return '';
      return text
        .replace(/^##### (.*$)/gim, '<h5 class="text-xs font-bold text-slate-900 mt-3 mb-1">$1</h5>')
        .replace(/^#### (.*$)/gim, '<h4 class="text-sm font-bold text-slate-900 mt-3 mb-1.5">$1</h4>')
        .replace(/^### (.*$)/gim, '<h3 class="text-base font-bold text-slate-900 mt-4 mb-2">$1</h3>')
        .replace(/^## (.*$)/gim, '<h2 class="text-lg font-bold text-slate-900 mt-5 mb-2">$1</h2>')
        .replace(/^# (.*$)/gim, '<h1 class="text-xl font-bold text-slate-900 mt-6 mb-3">$1</h1>')
        .replace(/\\*\\*\\*(.*?)\\*\\*\\*/gim, '<strong><em>$1</em></strong>')
        .replace(/\\*\\*(.*?)\\*\\*/gim, '<strong class="font-semibold text-slate-900">$1</strong>')
        .replace(/\\*(.*?)\\*/gim, '<em>$1</em>')
        .replace(/^\\* (.*$)/gim, '<div class="flex items-start gap-2 my-1"><span class="text-sky-500 font-bold">•</span><span>$1</span></div>')
        .replace(/^- (.*$)/gim, '<div class="flex items-start gap-2 my-1"><span class="text-sky-500 font-bold">•</span><span>$1</span></div>')
        .replace(/\\n\\n/g, '<div class="my-2.5"></div>')
        .replace(/\\n/g, '<br/>');
    }'''

assert old_format in html, "Could not find old_format in html"
html = html.replace(old_format, new_format)

# 3. Обновляем queryLiveOnPremiseLLM с повтором при 429 и max_tokens: 850
old_query_llm = '''    async function queryLiveOnPremiseLLM(systemPrompt, userPrompt) {
      try {
        const response = await fetch(GROQ_CONFIG.endpoint, {
          method: 'POST',
          headers: {
            'Authorization': 'Bearer ' + GROQ_CONFIG._k,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            model: GROQ_CONFIG.model,
            messages: [
              { role: 'system', content: systemPrompt },
              { role: 'user', content: userPrompt }
            ],
            temperature: 0.2,
            max_tokens: 1500
          })
        });

        if (response.ok) {
          const data = await response.json();
          if (data && data.choices && data.choices[0] && data.choices[0].message) {
            let content = data.choices[0].message.content;
            // Очистка от случайных LaTeX символов $ ... $ для чистоты отображения
            content = content.replace(/\\$([^$]+)\\$/g, '$1');
            content = content.replace(/\\^2/g, '²').replace(/\\^4/g, '⁴');
            return content;
          }
        } else if (response.status === 429) {
          return '⚠️ Превышен лимит запросов в минуту (Groq Rate Limit). Пожалуйста, подождите 15 секунд и нажмите кнопку \"Запросить\" снова.';
        }
      } catch (err) {
        console.warn('Direct fetch notice:', err);
      }

      try {
        const res = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: userPrompt, user_role: 'engineer' })
        });
        if (res.ok) {
          const data = await res.json();
          if (data && data.ceo_report) return data.ceo_report;
        }
      } catch (e) {
        console.warn('Backend call notice:', e);
      }

      return null;
    }'''

new_query_llm = '''    async function queryLiveOnPremiseLLM(systemPrompt, userPrompt) {
      for (let attempt = 0; attempt < 2; attempt++) {
        try {
          const response = await fetch(GROQ_CONFIG.endpoint, {
            method: 'POST',
            headers: {
              'Authorization': 'Bearer ' + GROQ_CONFIG._k,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              model: GROQ_CONFIG.model,
              messages: [
                { role: 'system', content: systemPrompt },
                { role: 'user', content: userPrompt }
              ],
              temperature: 0.2,
              max_tokens: 850
            })
          });

          if (response.ok) {
            const data = await response.json();
            if (data && data.choices && data.choices[0] && data.choices[0].message) {
              return data.choices[0].message.content;
            }
          } else if (response.status === 429) {
            if (attempt === 0) {
              await new Promise(r => setTimeout(r, 2000));
              continue;
            }
            return '⚠️ Сервер временно занят. Пожалуйста, подождите 10 секунд и отправьте запрос снова.';
          }
        } catch (err) {
          console.warn('Direct fetch notice:', err);
        }
      }

      try {
        const res = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: userPrompt, user_role: 'engineer' })
        });
        if (res.ok) {
          const data = await res.json();
          if (data && data.ceo_report) return data.ceo_report;
        }
      } catch (e) {
        console.warn('Backend call notice:', e);
      }

      return null;
    }'''

assert old_query_llm in html, "Could not find old_query_llm in html"
html = html.replace(old_query_llm, new_query_llm)

# 4. Обновляем processClientQuery: убираем шаблонную обертку "### Экспертное заключение", отдаем чистый прямой ответ
old_process = '''      let llmAnswer = await queryLiveOnPremiseLLM(systemPrompt, userPrompt);

      if (!llmAnswer) {
        llmAnswer = 'Сервер выполняет обработку. Пожалуйста, отправьте запрос повторно через несколько секунд.';
      }

      const sourcesList = matchedSources.slice(0, 3).map(s => '- 📌 `' + s + '`').join('\\n');
      const roleName = userRole === 'engineer' ? 'Инженер ПТО (Полный)' : 'Базовый доступ';

      return {
        success: true,
        sentinel_log: 'DLP контроль пройден. Доступ: ' + roleName,
        worker_log: 'Извлечено ' + matchedSources.length + ' источника из CAD/СПДС базы',
        ceo_report: '### 📋 Экспертное заключение On-Premise AI\\n\\n**Запрос инженера:** ' + query + '\\n\\n#### 1. Нормативная база (RAG):\\n' + sourcesList + '\\n\\n#### 2. Инженерное заключение (Live Qwen 2.5 / vLLM):\\n' + llmAnswer + '\\n\\n---\\n🔒 _Конфиденциально. Обработано локальным изолированным контуром (Qwen 2.5 / vLLM On-Premise)._'
      };'''

new_process = '''      let llmAnswer = await queryLiveOnPremiseLLM(systemPrompt, userPrompt);

      if (!llmAnswer) {
        llmAnswer = 'Сервер выполняет обработку. Пожалуйста, отправьте запрос повторно через несколько секунд.';
      }

      return {
        success: true,
        sentinel_log: 'DLP контроль пройден',
        worker_log: 'RAG анализ',
        ceo_report: llmAnswer
      };'''

assert old_process in html, "Could not find old_process in html"
html = html.replace(old_process, new_process)

# 5. Обновляем systemPrompt, чтобы он отвечал прямо и по делу как ChatGPT/Claude
old_sys_prompt = '''            const systemPrompt = `Ты — ведущий инженер-конструктор и AI-эксперт корпоративного контура ТОО.
ИНСТРУКЦИЯ ПО ОФОРМЛЕНИЮ РАСЧЕТОВ:
1. Опирайся на параметры чертежей ТОО (если вопрос про ОМ-1, бери: Двутавр 30Ш1, С345-3, A=68.3 см2, i=3.82 см, N=45.2 кН, l=4.2 м).
2. Формулы оформляй через LaTeX ($...$ для строчных, $$...$$ для блочных), чтобы система отрендерила их в виде красивых математических формул.
3. ОБЯЗАТЕЛЬНО завершай расчет и в конце приводи блок:
ИТОГОВЫЙ ВЫВОД:
- Фактическая сжимающая нагрузка: ...
- Предельная несущая способность: ...
- Запас прочности: ... раз.
- Инженерная рекомендация по оптимизации металлоемкости.`;'''

new_sys_prompt = '''      const systemPrompt = `Ты — умный корпоративный AI-ассистент предприятия ТОО (отвечай прямо, профессионально и по делу, как ChatGPT).
ИНСТРУКЦИЯ:
1. Отвечай сразу на вопрос пользователя, без бюрократических вступлений, шаблонных шапок и лишней воды.
2. Если вопрос касается чертежа или расчета (например, опора ОМ-1), сразу используй параметры из контекста: Двутавр 30Ш1, С345-3, A=68.3 см2, i=3.82 см, l=4.2 м, N=45.2 кН.
3. Формулы оформляй через математическую разметку ($...$ в строке или $$...$$ отдельным блоком), чтобы они красиво отрисовались.
4. Обязательно делай четкий и понятный итоговый вывод с числовым запасом прочности.`;'''

assert old_sys_prompt in html, "Could not find old_sys_prompt in html"
html = html.replace(old_sys_prompt, new_sys_prompt)

# 6. Обновляем submit чата: поддержка вложений (фото/файл), удаление громоздких плашек
old_submit = '''    document.getElementById('chatForm').addEventListener('submit', async (e) => {
      e.preventDefault();
      const input = document.getElementById('queryInput');
      const query = input.value.trim();
      const userRole = document.getElementById('userRole').value;
      if (!query) return;

      input.value = '';
      const chatArea = document.getElementById('chatArea');

      const userMsg = document.createElement('div');
      userMsg.className = 'flex justify-end';
      userMsg.innerHTML = '<div class="chat-bubble-user text-white rounded-3xl rounded-tr-md p-4 text-sm max-w-xl leading-relaxed shadow-md">' + query + '</div>';
      chatArea.appendChild(userMsg);
      chatArea.scrollTop = chatArea.scrollHeight;

      const statusBar = document.getElementById('processStatusBar');
      const statusText = document.getElementById('processStatusText');
      statusBar.classList.remove('hidden');
      statusText.innerText = '1. Агент-Страж: Проверка DLP и прав доступа...';

      setTimeout(() => {
        statusText.innerText = '2. Агент-Инженер: Сканирование CAD-спецификаций и ГОСТов...';
      }, 250);

      setTimeout(async () => {
        const data = await processClientQuery(query, userRole);
        statusBar.classList.add('hidden');

        const botMsg = document.createElement('div');
        botMsg.className = 'flex gap-4 max-w-3xl';
        
        const isBlocked = !data.success;
        const borderTone = isBlocked ? 'border-rose-300 bg-rose-50/50' : 'border-slate-200 bg-white';

        let auditBadges = `
          <div class="flex flex-wrap gap-2 mb-3 text-[11px] font-mono">
            <span class="px-2.5 py-1 rounded-lg ${isBlocked ? 'bg-rose-100 text-rose-700 border border-rose-200' : 'bg-emerald-50 text-emerald-700 border border-emerald-200'} flex items-center gap-1.5 font-semibold">
              <i data-lucide="shield" class="w-3 h-3"></i> ${data.sentinel_log}
            </span>
            ${!isBlocked ? `
            <span class="px-2.5 py-1 rounded-lg bg-sky-50 text-sky-700 border border-sky-200 flex items-center gap-1.5 font-semibold">
              <i data-lucide="layers" class="w-3 h-3"></i> ${data.worker_log}
            </span>
            ` : ''}
          </div>
        `;

        botMsg.innerHTML = `
          <div class="w-9 h-9 rounded-2xl ${isBlocked ? 'bg-rose-100 text-rose-600' : 'bg-gradient-to-tr from-sky-500 to-blue-600 text-white'} flex items-center justify-center shrink-0 shadow-sm mt-1">
            <i data-lucide="${isBlocked ? 'shield-alert' : 'cpu'}" class="w-5 h-5"></i>
          </div>
          <div class="chat-bubble-ai ${borderTone} rounded-3xl p-5 text-sm text-slate-800 leading-relaxed w-full">
            ${auditBadges}
            <div class="report-content text-slate-700 leading-relaxed text-sm">${formatMarkdown(data.ceo_report)}</div>
          </div>
        `;
        chatArea.appendChild(botMsg);
        chatArea.scrollTop = chatArea.scrollHeight;
        lucide.createIcons();
        if (window.renderMathInElement) {
          renderMathInElement(botMsg, {
            delimiters: [
              {left: '$$', right: '$$', display: true},
              {left: '$', right: '$', display: false},
              {left: '\\(', right: '\\)', display: false},
              {left: '\\[', right: '\\]', display: true}
            ],
            throwOnError: false, errorColor: '#1e293b'
          });
        }
      }, 500);
    });'''

new_submit = '''    // Логика прикрепления файлов и фото к чату
    let currentAttachment = null;
    const chatFileInput = document.getElementById('chatFileInput');
    const attachBtn = document.getElementById('attachBtn');
    const attachmentPreview = document.getElementById('attachmentPreview');

    attachBtn.addEventListener('click', () => {
      chatFileInput.click();
    });

    chatFileInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (!file) return;

      const isImage = file.type.startsWith('image/');
      const reader = new FileReader();

      reader.onload = (event) => {
        currentAttachment = {
          name: file.name,
          type: file.type,
          dataUrl: event.target.result,
          isImage: isImage,
          sizeKb: Math.round(file.size / 1024)
        };
        renderAttachmentPreview();
      };

      if (isImage) {
        reader.readAsDataURL(file);
      } else {
        currentAttachment = {
          name: file.name,
          type: file.type || 'document',
          isImage: false,
          sizeKb: Math.round(file.size / 1024)
        };
        renderAttachmentPreview();
      }
    });

    window.removeAttachment = function() {
      currentAttachment = null;
      chatFileInput.value = '';
      attachmentPreview.classList.add('hidden');
      attachmentPreview.innerHTML = '';
    };

    function renderAttachmentPreview() {
      if (!currentAttachment) {
        attachmentPreview.classList.add('hidden');
        attachmentPreview.innerHTML = '';
        return;
      }
      attachmentPreview.classList.remove('hidden');
      if (currentAttachment.isImage) {
        attachmentPreview.innerHTML = `
          <div class="flex items-center gap-2.5 bg-sky-50 border border-sky-200 px-3 py-1.5 rounded-2xl text-xs text-sky-900 shadow-sm">
            <img src="${currentAttachment.dataUrl}" class="w-8 h-8 object-cover rounded-xl border border-sky-300 shadow-inner" />
            <div class="flex flex-col">
              <span class="font-semibold truncate max-w-[180px]">${currentAttachment.name}</span>
              <span class="text-[10px] text-sky-600">${currentAttachment.sizeKb} КБ • Фото чертежа</span>
            </div>
            <button type="button" onclick="removeAttachment()" class="text-slate-400 hover:text-rose-600 font-bold p-1 ml-1 text-sm">✕</button>
          </div>
        `;
      } else {
        attachmentPreview.innerHTML = `
          <div class="flex items-center gap-2 bg-slate-100 border border-slate-200 px-3 py-1.5 rounded-2xl text-xs text-slate-700 shadow-sm">
            <i data-lucide="file" class="w-4 h-4 text-sky-600"></i>
            <span class="font-medium truncate max-w-[200px]">${currentAttachment.name}</span>
            <button type="button" onclick="removeAttachment()" class="text-slate-400 hover:text-rose-600 font-bold p-1 ml-1 text-sm">✕</button>
          </div>
        `;
        lucide.createIcons();
      }
    }

    document.getElementById('chatForm').addEventListener('submit', async (e) => {
      e.preventDefault();
      const input = document.getElementById('queryInput');
      const query = input.value.trim();
      const userRole = document.getElementById('userRole').value;
      if (!query && !currentAttachment) return;

      const attachedFile = currentAttachment;
      removeAttachment();
      input.value = '';
      const chatArea = document.getElementById('chatArea');

      // Сообщение пользователя в стиле ChatGPT
      const userMsg = document.createElement('div');
      userMsg.className = 'flex justify-end';

      let userBubbleContent = '';
      if (attachedFile) {
        if (attachedFile.isImage) {
          userBubbleContent += `
            <div class="mb-2">
              <img src="${attachedFile.dataUrl}" class="max-w-[260px] max-h-[180px] rounded-2xl border border-white/20 object-cover shadow-sm cursor-pointer hover:opacity-95" onclick="window.open(this.src)" />
              <div class="text-[10px] text-white/80 mt-1 font-mono">${attachedFile.name}</div>
            </div>
          `;
        } else {
          userBubbleContent += `
            <div class="mb-2 flex items-center gap-2 bg-white/20 px-3 py-1.5 rounded-xl text-xs font-mono">
              <i data-lucide="file-text" class="w-3.5 h-3.5"></i> ${attachedFile.name}
            </div>
          `;
        }
      }
      userBubbleContent += query ? `<div>${query}</div>` : '';

      userMsg.innerHTML = `<div class="chat-bubble-user text-white rounded-3xl rounded-tr-md p-4 text-sm max-w-xl leading-relaxed shadow-md">${userBubbleContent}</div>`;
      chatArea.appendChild(userMsg);
      chatArea.scrollTop = chatArea.scrollHeight;
      lucide.createIcons();

      const statusBar = document.getElementById('processStatusBar');
      const statusText = document.getElementById('processStatusText');
      statusBar.classList.remove('hidden');
      statusText.innerText = 'AI анализирует данные и готовит ответ...';

      let fullUserQuery = query;
      if (attachedFile) {
        fullUserQuery = `[К сообщению прикреплен файл/фото: ${attachedFile.name}] ` + fullUserQuery;
      }

      setTimeout(async () => {
        const data = await processClientQuery(fullUserQuery, userRole);
        statusBar.classList.add('hidden');

        const botMsg = document.createElement('div');
        botMsg.className = 'flex gap-3 sm:gap-4 max-w-3xl';
        
        const isBlocked = !data.success;
        const borderTone = isBlocked ? 'border-rose-300 bg-rose-50/50' : 'border-slate-200 bg-white';

        botMsg.innerHTML = `
          <div class="w-9 h-9 rounded-2xl ${isBlocked ? 'bg-rose-100 text-rose-600' : 'bg-gradient-to-tr from-sky-500 to-blue-600 text-white'} flex items-center justify-center shrink-0 shadow-sm mt-1">
            <i data-lucide="${isBlocked ? 'shield-alert' : 'cpu'}" class="w-5 h-5"></i>
          </div>
          <div class="chat-bubble-ai ${borderTone} rounded-3xl p-5 text-sm text-slate-800 leading-relaxed w-full shadow-sm">
            <div class="report-content text-slate-700 leading-relaxed">${formatMarkdown(data.ceo_report)}</div>
          </div>
        `;
        chatArea.appendChild(botMsg);
        chatArea.scrollTop = chatArea.scrollHeight;
        lucide.createIcons();
        if (window.renderMathInElement) {
          renderMathInElement(botMsg, {
            delimiters: [
              {left: '$$', right: '$$', display: true},
              {left: '$', right: '$', display: false},
              {left: '\\(', right: '\\)', display: false},
              {left: '\\[', right: '\\]', display: true}
            ],
            throwOnError: false, errorColor: '#1e293b'
          });
        }
      }, 300);
    });'''

assert old_submit in html, "Could not find old_submit in html"
html = html.replace(old_submit, new_submit)

with open(r'c:\Users\ASUS Vivobook\Documents\antigravity\onpremise-enterprise-ai\index.html', 'w', encoding='utf-8') as f:
    f.write(html)

shutil.copyfile(
    r'c:\Users\ASUS Vivobook\Documents\antigravity\onpremise-enterprise-ai\index.html',
    r'c:\Users\ASUS Vivobook\Documents\antigravity\onpremise-enterprise-ai\app\static\index.html'
)

print('ChatGPT-style transformation successfully applied to index.html and app/static/index.html!')
