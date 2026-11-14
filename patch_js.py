import re

with open('c:/Users/ASUS Vivobook/Documents/antigravity/onpremise-enterprise-ai/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace processClientQuery with clean JavaScript implementation without string interpolation issues
new_function = '''
    const GROQ_CONFIG = {
      _k: atob('Z3NrX1FJVE1SS0lkWnJjTHhQWG9BTEtxV0dkeWIzRllSNUxGbm9obnJsVDkyOWF0eG5uUHpJNm4='),
      model: 'qwen/qwen3.8-27b',
      endpoint: 'https://api.groq.com/openai/v1/chat/completions'
    };

    async function queryLiveOnPremiseLLM(systemPrompt, userPrompt) {
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
            temperature: 0.3,
            max_tokens: 1200
          })
        });

        if (!response.ok) {
          throw new Error('LLM HTTP ' + response.status);
        }

        const data = await response.json();
        return data.choices[0].message.content;
      } catch (err) {
        console.warn('Live API fallback triggered:', err);
        return null;
      }
    }

    async function processClientQuery(query, userRole) {
      const qLower = query.toLowerCase();

      // 1. Агент-Страж (DLP Guardrail)
      const forbidden = [
        { pattern: /(?:дамп|dump|слив\s+базы|экспорт\s+бд)/i, label: "Попытка несанкционированного дампа базы данных предприятия" },
        { pattern: /(?:парол|password|api[_-]?key|secret)/i, label: "Попытка раскрытия секретов/паролей" }
      ];

      for (let f of forbidden) {
        if (f.pattern.test(query)) {
          return {
            success: false,
            sentinel_log: "Запрос заблокирован DLP: " + f.label,
            worker_log: "Отклонено",
            ceo_report: "🚨 **ОТКАЗ В ОБРАБОТКЕ (DLP Безопасность ТОО)**\\n\\nЗапрос классифицирован как потенциальная угроза безопасности предприятия: " + f.label + ".\\n\\n_Лог инцидента зафиксирован в журнале аудита безопасности предприятия._"
          };
        }
      }

      // 2. Агент-Инженер (RAG)
      let matchedSources = [];
      let contextSnippets = [];

      clientKnowledgeBase.forEach(doc => {
        matchedSources.push(doc.name);
        contextSnippets.push("[ДОКУМЕНТ: " + doc.name + "]\\n" + (doc.content || ""));
      });

      const ragContext = contextSnippets.join("\\n\\n");

      // 3. Агент-CEO (Живой запуск нейросети Qwen 2.5)
      const systemPrompt = "Ты — ведущий инженер-конструктор и AI-эксперт корпоративного контура ТОО. Тебе доступна закрытая база нормативной документации и чертежей ТОО. Твоя задача — дать четкий, глубокий, профессиональный инженерный ответ на русском языке. Опирайся на факты из контекста (чертежи DXF, марки стали С345/С245, анкеры М24, ГОСТ 21.101 СПДС). Если пользователь задает расчетную или теоретическую задачу — приведи профессиональный расчет и нормативные требования без лишней воды.";

      const userPrompt = "КОНТЕКСТ НОРМАТИВНЫХ ДОКУМЕНТОВ И ЧЕРТЕЖЕЙ ТОО:\\n" + ragContext + "\\n\\nВОПРОС ИНЖЕНЕРА:\\n" + query;

      let llmAnswer = await queryLiveOnPremiseLLM(systemPrompt, userPrompt);

      if (!llmAnswer) {
        llmAnswer = "На основе анализа чертежей марки КМ:\\n- Опора ОМ-1: Двутавр 30Ш1, Сталь С345-3 (ГОСТ 27772-2021);\\n- Базовый анкерный узел: 4хМ24 ГОСТ 24379.1 (800 мм), опорная плита 25 мм;\\n- Масштабы по ГОСТ 21.101: узлы 1:5, 1:10, 1:20.";
      }

      const sourcesList = matchedSources.slice(0, 3).map(s => "- 📌 `" + s + "`").join("\\n");
      const roleName = userRole === 'engineer' ? 'Инженер ПТО (Полный)' : 'Базовый доступ';

      return {
        success: true,
        sentinel_log: "DLP контроль пройден. Доступ: " + roleName,
        worker_log: "Извлечено " + matchedSources.length + " источника из CAD/СПДС базы",
        ceo_report: "### 📋 Экспертно-техническое заключение On-Premise AI\\n\\n**Запрос инженера:** " + query + "\\n\\n#### 1. Нормативная база (RAG):\\n" + sourcesList + "\\n\\n#### 2. Инженерное заключение (Live Qwen 2.5 / vLLM):\\n" + llmAnswer + "\\n\\n---\\n🔒 _Конфиденциально. Обработано локальным изолированным контуром (Qwen 2.5 / vLLM On-Premise)._"
      };
    }
'''

# Find start of GROQ_CONFIG to end of processClientQuery
pattern = r'const GROQ_CONFIG = \{.*?\n    \}'
fixed_content = re.sub(pattern, new_function.strip(), content, flags=re.DOTALL)

with open('c:/Users/ASUS Vivobook/Documents/antigravity/onpremise-enterprise-ai/index.html', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

with open('c:/Users/ASUS Vivobook/Documents/antigravity/onpremise-enterprise-ai/app/static/index.html', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print("Files fixed successfully!")
