// ==UserScript==
// @name         AFL Bridge - AI Studio & Antigravity Autonomous Link
// @namespace    http://tampermonkey.net/
// @version      6.1.0
// @description  AFL v6.1.0 Autonomous Link: Single-source physical click, macro-task state stabilization & multi-turn seamless concatenation!
// @author       Jin Xiao (槿潇) & Argon Commander
// @match        https://aistudio.google.com/*
// @grant        GM_xmlhttpRequest
// @connect      127.0.0.1
// @run-at       document-idle
// ==/UserScript==

(function () {
    'use strict';

    if (window.self !== window.top) return;

    const BRIDGE_HOST = 'http://127.0.0.1:8790';
    const EOF_BEACON_TOKEN = '[AFL_EOF_' + 'ACK]';
    const EOF_TAIL_REGEX = new RegExp('\\[AFL_EOF_' + 'ACK\\]\\s*(?:-->)?\\s*`{0,3}\\s*$');
    const EOF_STRIP_REGEX = new RegExp('(?:<!--\\s*)?`{0,3}\\[AFL_EOF_' + 'ACK\\]`{0,3}(?:\\s*-->)?\\s*$', 'g');

    const MAX_AUTO_RETRIES = 2;
    const QUIET_COUNTDOWN_DURATION_MS = 2200;
    const FLIGHT_GRACE_PERIOD_MS = 10000;
    const RETRY_BACKOFF_DELAY_MS = 3500;
    const MAX_FILE_UPLOAD_WAIT_MS = 90000;

    const NATIVE_SAFE_EXTENSIONS = new Set([
        '.txt', '.md', '.py', '.js', '.ts', '.html', '.css', '.csv', '.json', '.xml',
        '.pdf', '.png', '.jpg', '.jpeg', '.webp', '.heic', '.heif',
        '.wav', '.mp3', '.aiff', '.aac', '.ogg', '.flac',
        '.mp4', '.mpeg', '.mov', '.avi', '.flv', '.mpg', '.webm', '.wmv', '.3gpp'
    ]);

    const CAPSULE_SIGNATURES = [
        '【AFL',
        '咨询胶囊】',
        '战略咨询胶囊',
        '呈报对象',
        '呈报方',
        '呈报端',
        '[AFL_READY_FOR_DECISION]',
        '[AFL_TICKET:',
        '[AFL_CAPSULE]',
        '--- START OF FILE ',
        '【玄栖阁净室',
        '【当期名著原典',
        '【红与黑',
        '【净室',
        '净室文学伴读',
        '【AFL 净室名著伴读',
        EOF_BEACON_TOKEN
    ];

    const MANUAL_DISPATCH_TRIGGERS = [
        '#回传执行官',
        '#发回本地',
        '[AFL_DISPATCH]'
    ];

    let isBridgeActive = true;
    let isGenerating = false;
    let autoIterationCount = 0;
    let isScriptInjecting = false;
    let isTaskInjecting = false;
    const dispatchedTicketIds = new Set();

    let generationPhase = 'IDLE';
    let quietCountdownStart = 0;
    let lastObservedResponseText = '';
    let lastAttemptTimestamp = 0;
    let retryBackoffStart = 0;
    let cachedAwaitingTicket = null;

    let isIpcPulseInFlight = false;
    let lastPollTs = 0;
    let lastHeartbeatTs = 0;
    let lastHudTs = 0;

    console.log('[AFL_BRIDGE] Initializing AFL Bridge v6.1.0 (Single-Source Physical Click & Macro-Task State Stabilization)...');

    // -------------------------------------------------------------
    // 1. 防窗口被挡与后台标签页休眠锁 (Shared WebLock + 扩展 IPC 轮询)
    // -------------------------------------------------------------
    function initAntiOcclusionLock() {
        if (navigator.locks && navigator.locks.request) {
            try {
                navigator.locks.request('afl_commander_keepalive', { mode: 'shared' }, () => {
                    return new Promise(() => {});
                }).catch(() => {});
            } catch (e) {}
        }
    }

    function isElementVisible(el) {
        if (!el || el.hasAttribute('hidden')) return false;
        try {
            const st = window.getComputedStyle(el);
            if (st.display === 'none' || st.visibility === 'hidden' || st.opacity === '0') {
                return false;
            }
        } catch (e) {}
        return true;
    }

    function hasTrailingEofBeacon(text) {
        if (!text || text.length < 20) return false;
        const tailSlice = text.slice(-60).trim();
        return EOF_TAIL_REGEX.test(tailSlice);
    }

    // -------------------------------------------------------------
    // 2. 主君手动输入起源侦测器
    // -------------------------------------------------------------
    function hasCapsuleSignature(text) {
        if (!text) return false;
        for (const sig of CAPSULE_SIGNATURES) {
            if (text.includes(sig)) return true;
        }
        for (const trig of MANUAL_DISPATCH_TRIGGERS) {
            if (text.includes(trig)) return true;
        }
        const savedSnippet = sessionStorage.getItem('AFL_ACTIVE_PROMPT_SNIPPET') || (cachedAwaitingTicket && cachedAwaitingTicket.prompt_snippet) || '';
        if (savedSnippet && savedSnippet.length >= 15) {
            const cleanSnippet = savedSnippet.replace(/[#*`\n\r[\]()]/g, ' ').replace(/\s+/g, ' ').trim();
            const cleanText = text.replace(/[#*`\n\r[\]()]/g, ' ').replace(/\s+/g, ' ').trim();
            if (cleanSnippet.length >= 10 && cleanText.includes(cleanSnippet.slice(0, 25))) {
                return true;
            }
        }
        return false;
    }

    function initManualInputInterception() {
        document.addEventListener('keydown', (e) => {
            if (isScriptInjecting || generationPhase === 'PHASE_UPLOADING_FILES') return;
            if (e.key === 'Enter' && (e.ctrlKey || e.metaKey || !e.shiftKey)) {
                const inputEl = findInputTextarea();
                if (inputEl && (document.activeElement === inputEl || inputEl.contains(document.activeElement))) {
                    const val = (inputEl.value || inputEl.textContent || '').trim();
                    if (val.length > 0) {
                        if (hasCapsuleSignature(val)) {
                            sessionStorage.setItem('AFL_LAST_RUN_ORIGIN', 'AUTOMATED_CAPSULE');
                        } else {
                            sessionStorage.setItem('AFL_LAST_RUN_ORIGIN', 'MANUAL_HUMAN');
                            generationPhase = 'PHASE_HUMAN_CHAT_BYPASS';
                            updateHUDStatus();
                        }
                    }
                }
            }
        }, true);

        document.addEventListener('click', (e) => {
            if (isScriptInjecting || generationPhase === 'PHASE_UPLOADING_FILES') return;
            const btn = e.target.closest ? e.target.closest('button, ms-run-button') : null;
            if (!btn) return;
            const label = ((btn.getAttribute('aria-label') || '') + ' ' + (btn.textContent || '')).toLowerCase();
            if (label.includes('run') && !label.includes('rerun')) {
                const inputEl = findInputTextarea();
                const val = inputEl ? (inputEl.value || inputEl.textContent || '').trim() : '';
                if (val.length > 0 && !hasCapsuleSignature(val)) {
                    sessionStorage.setItem('AFL_LAST_RUN_ORIGIN', 'MANUAL_HUMAN');
                    generationPhase = 'PHASE_HUMAN_CHAT_BYPASS';
                    updateHUDStatus();
                } else if (hasCapsuleSignature(val)) {
                    sessionStorage.setItem('AFL_LAST_RUN_ORIGIN', 'AUTOMATED_CAPSULE');
                }
            }
        }, true);
    }

    // -------------------------------------------------------------
    // 3. 会话标题识别与持久化存储
    // -------------------------------------------------------------
    function getPromptTitle() {
        const titleSelectors = [
            'input.prompt-title',
            'input[aria-label="Prompt name"]',
            'input[aria-label*="title" i]',
            'input[placeholder="Untitled prompt"]',
            'ms-prompt-title input',
            'header input[type="text"]'
        ];
        for (const sel of titleSelectors) {
            const el = document.querySelector(sel);
            if (el && el.value && el.value.trim()) {
                return el.value.trim();
            }
        }

        const titleElem = document.querySelector('ms-prompt-title, .prompt-title-text, h1.prompt-title');
        if (titleElem && titleElem.textContent && titleElem.textContent.trim()) {
            const txt = titleElem.textContent.trim();
            if (txt && !txt.toLowerCase().includes('untitled')) {
                return txt;
            }
        }

        let docTitle = document.title || '';
        docTitle = docTitle.replace(/^Google AI Studio\s*[-–—:|]\s*/i, '');
        docTitle = docTitle.replace(/\s*[-–—:|]\s*Google AI Studio$/i, '');
        docTitle = docTitle.trim();
        if (docTitle && docTitle !== 'Google AI Studio') {
            return docTitle;
        }
        return 'Untitled';
    }

    function isCommanderTab() {
        const manual = sessionStorage.getItem('AFL_IS_COMMANDER_TAB');
        if (manual === 'true') return true;
        if (manual === 'false') return false;
        const currentTitle = getPromptTitle();
        return Boolean(currentTitle && currentTitle !== 'Untitled');
    }

    function simpleHash(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            hash = ((hash << 5) - hash) + str.charCodeAt(i);
            hash |= 0;
        }
        return String(hash);
    }

    function getDispatchedHash() {
        const title = getPromptTitle();
        try {
            return localStorage.getItem(`AFL_DISPATCHED_HASH_${title}`) || sessionStorage.getItem('AFL_LAST_PROCESSED_HASH') || '';
        } catch (e) {
            return '';
        }
    }

    function setDispatchedHash(hash) {
        const title = getPromptTitle();
        try {
            localStorage.setItem(`AFL_DISPATCHED_HASH_${title}`, hash);
            sessionStorage.setItem('AFL_LAST_PROCESSED_HASH', hash);
        } catch (e) {}
    }

    function getRetryCount(ticketId) {
        if (!ticketId) return 0;
        try {
            return parseInt(sessionStorage.getItem(`AFL_RETRY_COUNT_${ticketId}`) || '0', 10);
        } catch (e) {
            return 0;
        }
    }

    function setRetryCount(ticketId, count) {
        if (!ticketId) return;
        try {
            sessionStorage.setItem(`AFL_RETRY_COUNT_${ticketId}`, String(count));
        } catch (e) {}
    }

    function reportStatusToBridge(eventType, detailObj) {
        const currentTitle = getPromptTitle();
        const activeTicket = sessionStorage.getItem('AFL_ACTIVE_TICKET') || (cachedAwaitingTicket && cachedAwaitingTicket.id) || '';
        GM_xmlhttpRequest({
            method: 'POST',
            url: `${BRIDGE_HOST}/api/bridge/report_status`,
            headers: { 'Content-Type': 'application/json' },
            data: JSON.stringify({
                event: eventType,
                ticket_id: activeTicket,
                source_title: currentTitle,
                detail: detailObj || {}
            })
        });
    }

    // -------------------------------------------------------------
    // 4. 浮动状态 HUD UI
    // -------------------------------------------------------------
    function createFloatingHUD() {
        if (!document.body) return;
        if (document.getElementById('afl-bridge-hud')) {
            updateHUDStatus();
            return;
        }

        const hud = document.createElement('div');
        hud.id = 'afl-bridge-hud';
        hud.style.cssText = `
            position: fixed;
            bottom: 24px;
            right: 24px;
            z-index: 999999;
            background: rgba(30, 30, 36, 0.95);
            border: 1px solid #61afef;
            border-radius: 8px;
            padding: 12px 16px;
            color: #abb2bf;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace;
            font-size: 13px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
            display: flex;
            flex-direction: column;
            gap: 8px;
            min-width: 300px;
            max-width: 400px;
            backdrop-filter: blur(8px);
        `;

        const row1 = document.createElement('div');
        row1.style.cssText = 'display:flex; justify-content:space-between; align-items:center;';

        const title = document.createElement('span');
        title.style.cssText = 'font-weight:bold; color:#61afef;';
        title.textContent = '⚡ AFL v6.0 精简防遮挡版';

        const indicator = document.createElement('span');
        indicator.id = 'afl-status-indicator';
        indicator.style.cssText = 'font-size:11px; padding:2px 6px; border-radius:4px; background:#98c379; color:#1e1e24; font-weight:bold;';
        indicator.textContent = 'READY';

        row1.appendChild(title);
        row1.appendChild(indicator);

        const row2 = document.createElement('div');
        row2.style.cssText = 'font-size:12px; color:#abb2bf; display:flex; justify-content:space-between; align-items:center; background:#21252b; padding:6px 8px; border-radius:4px; gap:8px;';

        const sessionLabel = document.createElement('span');
        sessionLabel.id = 'afl-session-label';
        sessionLabel.style.cssText = 'white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:215px;';
        sessionLabel.textContent = `🎯 [${getPromptTitle()}]`;

        const sessionToggle = document.createElement('button');
        sessionToggle.id = 'afl-session-toggle';
        sessionToggle.style.cssText = 'background:none; border:none; color:#61afef; cursor:pointer; font-size:11px; text-decoration:underline; flex-shrink:0;';
        sessionToggle.textContent = isCommanderTab() ? '解绑' : '锁定';

        row2.appendChild(sessionLabel);
        row2.appendChild(sessionToggle);

        const row3 = document.createElement('div');
        row3.style.cssText = 'font-size:12px; color:#5c6370; display:flex; justify-content:space-between;';

        const roundLabel = document.createElement('span');
        roundLabel.id = 'afl-substatus-label';
        roundLabel.textContent = '状态: 待命';

        const roundCount = document.createElement('span');
        roundCount.id = 'afl-round-count';
        roundCount.style.cssText = 'color:#e5c07b; font-weight:bold;';
        roundCount.textContent = `轮次: 0`;

        row3.appendChild(roundLabel);
        row3.appendChild(roundCount);

        const row4 = document.createElement('div');
        row4.style.cssText = 'display:flex; gap:6px; margin-top:4px;';

        const toggleBtn = document.createElement('button');
        toggleBtn.id = 'afl-toggle-btn';
        toggleBtn.style.cssText = 'flex:1; background:#4b5263; color:#fff; border:none; padding:4px 8px; border-radius:4px; cursor:pointer; font-size:11px;';
        toggleBtn.textContent = '暂停路由';

        const forceCatchBtn = document.createElement('button');
        forceCatchBtn.id = 'afl-force-catch-btn';
        forceCatchBtn.style.cssText = 'background:#61afef; color:#1e1e24; font-weight:bold; border:none; padding:4px 8px; border-radius:4px; cursor:pointer; font-size:11px;';
        forceCatchBtn.textContent = '钦定回传末条';

        row4.appendChild(toggleBtn);
        row4.appendChild(forceCatchBtn);

        hud.appendChild(row1);
        hud.appendChild(row2);
        hud.appendChild(row3);
        hud.appendChild(row4);
        document.body.appendChild(hud);

        sessionToggle.addEventListener('click', () => {
            const current = isCommanderTab();
            sessionStorage.setItem('AFL_IS_COMMANDER_TAB', String(!current));
            updateHUDStatus();
        });

        toggleBtn.addEventListener('click', () => {
            isBridgeActive = !isBridgeActive;
            updateHUDStatus();
        });

        forceCatchBtn.addEventListener('click', () => {
            const txt = getLatestModelResponseText().trim();
            if (txt.length > 15) {
                sessionStorage.setItem('AFL_LAST_RUN_ORIGIN', 'AUTOMATED_CAPSULE');
                finalizeAndDispatchReply(txt, true);
            }
        });

        updateHUDStatus();
    }

    function updateHUDStatus() {
        const indicator = document.getElementById('afl-status-indicator');
        const sessionLabel = document.getElementById('afl-session-label');
        const sessionToggle = document.getElementById('afl-session-toggle');
        const substatusLabel = document.getElementById('afl-substatus-label');
        const toggleBtn = document.getElementById('afl-toggle-btn');
        const hud = document.getElementById('afl-bridge-hud');

        if (!hud) return;

        const isCommander = isCommanderTab();
        const currentTitle = getPromptTitle();
        const activeTicket = sessionStorage.getItem('AFL_ACTIVE_TICKET') || '';
        const retryCount = getRetryCount(activeTicket);
        const lastOrigin = sessionStorage.getItem('AFL_LAST_RUN_ORIGIN') || '';

        if (sessionLabel) {
            sessionLabel.textContent = isCommander ? `👑 [${currentTitle}]` : `💤 [${currentTitle}] (未路由)`;
            sessionLabel.style.color = isCommander ? '#98c379' : '#5c6370';
            sessionLabel.title = currentTitle;
        }
        if (sessionToggle) {
            sessionToggle.textContent = isCommander ? '解绑' : '锁定';
        }

        if (!isCommander) {
            hud.style.borderColor = '#5c6370';
            hud.style.opacity = '0.7';
            if (indicator) {
                indicator.textContent = 'STANDBY';
                indicator.style.background = '#5c6370';
            }
            return;
        }

        hud.style.opacity = '1.0';

        if (!isBridgeActive) {
            hud.style.borderColor = '#e06c75';
            if (indicator) {
                indicator.textContent = 'PAUSED';
                indicator.style.background = '#e06c75';
            }
            if (toggleBtn) {
                toggleBtn.textContent = '恢复路由';
                toggleBtn.style.background = '#98c379';
            }
            return;
        }

        if (toggleBtn) {
            toggleBtn.textContent = '暂停路由';
            toggleBtn.style.background = '#4b5263';
        }

        if (generationPhase === 'PHASE_UPLOADING_FILES') {
            hud.style.borderColor = '#d19a66';
            if (indicator) {
                indicator.textContent = '📎 上传解析附件中';
                indicator.style.background = '#d19a66';
            }
            if (substatusLabel) {
                substatusLabel.textContent = '等待文件转圈结束与 Run 解禁...';
                substatusLabel.style.color = '#d19a66';
            }
        } else if (generationPhase === 'PHASE_HUMAN_CHAT_BYPASS' || lastOrigin === 'MANUAL_HUMAN') {
            hud.style.borderColor = '#56b6c2';
            if (indicator) {
                indicator.textContent = '💬 主君私聊 (免打扰)';
                indicator.style.background = '#56b6c2';
            }
            if (substatusLabel) {
                substatusLabel.textContent = activeTicket ? `已挂起保护票据: ${activeTicket.slice(-8)}` : '主君自由对话中 (不回传)';
                substatusLabel.style.color = '#56b6c2';
            }
        } else if (generationPhase === 'PHASE_MANUAL_AWAITED') {
            hud.style.borderColor = '#e5c07b';
            if (indicator) {
                indicator.textContent = `📱 待接力 (${retryCount}/${MAX_AUTO_RETRIES})`;
                indicator.style.background = '#e5c07b';
            }
            if (substatusLabel) {
                substatusLabel.textContent = '请手机重跑后F5刷新或手动重试';
                substatusLabel.style.color = '#e5c07b';
            }
        } else if (generationPhase === 'PHASE1_GENERATING') {
            hud.style.borderColor = '#c678dd';
            if (indicator) {
                indicator.textContent = retryCount > 0 ? `THINKING (重试${retryCount})` : 'THINKING';
                indicator.style.background = '#c678dd';
            }
            if (substatusLabel) {
                substatusLabel.textContent = '云端推演中 (Win32后台护航)...';
                substatusLabel.style.color = '#c678dd';
            }
        } else if (activeTicket) {
            hud.style.borderColor = '#61afef';
            if (indicator) {
                indicator.textContent = 'AWAITING';
                indicator.style.background = '#61afef';
            }
            if (substatusLabel) {
                substatusLabel.textContent = `执牌守候: ${activeTicket.slice(-10)}`;
                substatusLabel.style.color = '#61afef';
            }
        } else {
            hud.style.borderColor = '#61afef';
            if (indicator) {
                indicator.textContent = 'ACTIVE';
                indicator.style.background = '#98c379';
            }
            if (substatusLabel) {
                substatusLabel.textContent = '状态: 防遮挡巡航待命';
                substatusLabel.style.color = '#abb2bf';
            }
        }
    }

    // -------------------------------------------------------------
    // 5. 工程文件反序列化与三级级联注盘
    // -------------------------------------------------------------
    function convertAttachmentToFile(att) {
        const binaryString = window.atob(att.content_b64 || '');
        const len = binaryString.length;
        const bytes = new Uint8Array(len);
        for (let i = 0; i < len; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }

        let fileName = att.name || 'attachment.txt';
        const dotIdx = fileName.lastIndexOf('.');
        const ext = dotIdx >= 0 ? fileName.slice(dotIdx).toLowerCase() : '';
        let mimeType = att.mime_type || 'text/plain';

        if (att.is_text) {
            mimeType = 'text/plain';
            if (!NATIVE_SAFE_EXTENSIONS.has(ext)) {
                fileName = `${fileName}.txt`;
            }
        }

        const blob = new Blob([bytes], { type: mimeType });
        return new File([blob], fileName, { type: mimeType, lastModified: Date.now() });
    }

    function getPromptComposerContainer() {
        const inputEl = findInputTextarea();
        if (inputEl) {
            const box = inputEl.closest('ms-prompt-box, .prompt-box-container, ms-chunk-editor, .input-container, footer');
            if (box) return box;
        }
        return document.querySelector('ms-prompt-box, .prompt-box-container, ms-chunk-editor, footer') || document.body;
    }

    function countComposerFileChips() {
        const composer = getPromptComposerContainer();
        const chipSelectors = [
            'ms-media-chunk', 'ms-file-chunk', 'ms-chip', 'mat-chip', 'mat-chip-row',
            '.media-chunk', '.file-chip', '.attachment-chip',
            '[class*="file-chip"]', '[class*="media-chunk"]', '[class*="prompt-chip"]'
        ].join(', ');

        return Array.from(composer.querySelectorAll(chipSelectors)).filter(
            el => !el.closest('ms-chat-turn') && isElementVisible(el)
        ).length;
    }

    function isComposerStillUploadingFiles() {
        const composer = getPromptComposerContainer();
        const spinnerSelectors = 'mat-progress-spinner, mat-spinner, mat-progress-bar, .spinner, .loading-spinner, [aria-busy="true"], [class*="uploading"]';
        const spinners = Array.from(composer.querySelectorAll(spinnerSelectors)).filter(
            el => !el.closest('ms-chat-turn') && isElementVisible(el)
        );
        if (spinners.length > 0) return true;

        const chips = Array.from(composer.querySelectorAll('ms-media-chunk, ms-file-chunk, mat-chip-row, [class*="chip"]')).filter(
            el => !el.closest('ms-chat-turn') && isElementVisible(el)
        );
        for (const chip of chips) {
            const txt = (chip.textContent || '').toLowerCase();
            if (txt.includes('uploading') || txt.includes('processing') || txt.includes('extracting') || txt.includes('上传')) {
                return true;
            }
        }
        return false;
    }

    function detectAttachmentUploadError() {
        const alerts = Array.from(document.querySelectorAll('mat-snack-bar-container, [role="alert"], .mat-mdc-snack-bar-label'));
        for (const al of alerts) {
            if (!isElementVisible(al)) continue;
            const txt = (al.textContent || '').trim();
            if (/(unsupported|failed to upload|unable to upload|file is too large|invalid file)/i.test(txt)) {
                return txt;
            }
        }
        return null;
    }

    function findRunButton() {
        return document.querySelector(
            "ms-run-button button.run-button, ms-run-button button[type='submit'], ms-run-button button, button.run-button"
        );
    }

    function isRunButtonInStopState(btn) {
        const runBtn = btn || findRunButton();
        if (!runBtn || runBtn.disabled || !isElementVisible(runBtn)) return false;
        if (runBtn.classList.contains('stoppable')) return true;
        const aria = (runBtn.getAttribute('aria-label') || '').trim().toLowerCase();
        if (aria === 'stop' || aria.startsWith('stop ') || aria.includes('停止')) return true;
        return false;
    }

    function isRunButtonUnlocked() {
        const btn = findRunButton();
        if (!btn) return false;
        const host = btn.closest('ms-run-button');
        const isHostDisabled = host && (host.hasAttribute('disabled') || host.getAttribute('aria-disabled') === 'true' || host.classList.contains('mat-mdc-button-disabled'));
        const isBtnDisabled = btn.disabled || btn.getAttribute('aria-disabled') === 'true' || btn.classList.contains('mat-mdc-button-disabled');
        return !isHostDisabled && !isBtnDisabled;
    }

    function unlockRunButton(btn) {
        if (!btn) return;
        try {
            if (btn.hasAttribute('disabled')) {
                btn.removeAttribute('disabled');
            }
            btn.disabled = false;
            if (btn.getAttribute('aria-disabled') === 'true') {
                btn.setAttribute('aria-disabled', 'false');
            }
            btn.classList.remove('mat-mdc-button-disabled', 'button-disabled', 'disabled');

            const host = btn.closest('ms-run-button');
            if (host) {
                if (host.hasAttribute('disabled')) host.removeAttribute('disabled');
                if (host.getAttribute('aria-disabled') === 'true') host.setAttribute('aria-disabled', 'false');
                host.classList.remove('mat-mdc-button-disabled', 'button-disabled', 'disabled');
            }
        } catch (e) {}
    }

    function injectFilesCascading(fileObjects, callback) {
        const beforeChips = countComposerFileChips();
        const inputEl = findInputTextarea();
        const composer = getPromptComposerContainer();

        const dt = new DataTransfer();
        for (const f of fileObjects) {
            dt.items.add(f);
        }

        if (inputEl) {
            try { inputEl.focus(); } catch (e) {}
            let pasteEvt;
            try {
                pasteEvt = new ClipboardEvent('paste', {
                    bubbles: true, cancelable: true, composed: true, clipboardData: dt
                });
                if (!pasteEvt.clipboardData || pasteEvt.clipboardData.files.length === 0) {
                    Object.defineProperty(pasteEvt, 'clipboardData', { value: dt });
                }
            } catch (e) {
                pasteEvt = new Event('paste', { bubbles: true, cancelable: true, composed: true });
                Object.defineProperty(pasteEvt, 'clipboardData', { value: dt });
            }
            inputEl.dispatchEvent(pasteEvt);
        }

        setTimeout(() => {
            if (countComposerFileChips() > beforeChips || isComposerStillUploadingFiles()) {
                callback({ mounted: true, method: 'Tier1_ClipboardPaste' });
                return;
            }

            const dropTargets = [composer, inputEl].filter(Boolean);
            for (const target of dropTargets) {
                for (const evtName of ['dragenter', 'dragover', 'drop']) {
                    let dragEvt;
                    try {
                        dragEvt = new DragEvent(evtName, {
                            bubbles: true, cancelable: true, composed: true, dataTransfer: dt
                        });
                        if (!dragEvt.dataTransfer || dragEvt.dataTransfer.files.length === 0) {
                            Object.defineProperty(dragEvt, 'dataTransfer', { value: dt });
                        }
                    } catch (e) {
                        dragEvt = new Event(evtName, { bubbles: true, cancelable: true, composed: true });
                        Object.defineProperty(dragEvt, 'dataTransfer', { value: dt });
                    }
                    target.dispatchEvent(dragEvt);
                }
            }

            setTimeout(() => {
                if (countComposerFileChips() > beforeChips || isComposerStillUploadingFiles()) {
                    callback({ mounted: true, method: 'Tier2_DragDrop' });
                    return;
                }

                const fileInputs = Array.from(document.querySelectorAll('input[type="file"]'));
                if (fileInputs.length > 0) {
                    const fInput = fileInputs[fileInputs.length - 1];
                    try {
                        const protoSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'files')?.set;
                        if (protoSetter) protoSetter.call(fInput, dt.files);
                        else fInput.files = dt.files;
                        fInput.dispatchEvent(new Event('input', { bubbles: true, composed: true }));
                        fInput.dispatchEvent(new Event('change', { bubbles: true, composed: true }));
                    } catch (e) {}

                    setTimeout(() => {
                        if (countComposerFileChips() > beforeChips || isComposerStillUploadingFiles()) {
                            callback({ mounted: true, method: 'Tier3_FileInput' });
                        } else {
                            callback({ mounted: false, method: 'None' });
                        }
                    }, 400);
                } else {
                    callback({ mounted: false, method: 'None' });
                }
            }, 400);
        }, 400);
    }

    function buildInlineFallbackText(attachments, originalConsultText) {
        const blocks = [];
        for (const att of attachments) {
            if (att.is_text && att.text_content) {
                blocks.push(
                    `--- START OF FILE ${att.name} ---\n` +
                    `${att.text_content}\n` +
                    `--- END OF FILE ${att.name} ---`
                );
            }
        }
        if (blocks.length === 0) return originalConsultText;
        return `${blocks.join('\n\n')}\n\n${originalConsultText}`;
    }

    // -------------------------------------------------------------
    // 6. 精准底部输入框定位与同步击发
    // -------------------------------------------------------------
    function findInputTextarea() {
        const directBottom = document.querySelector(
            'ms-prompt-input-wrapper textarea, ms-chunk-input textarea, .prompt-input-wrapper textarea, footer textarea'
        );
        if (directBottom && !directBottom.disabled) {
            return directBottom;
        }

        const allTextareas = Array.from(document.querySelectorAll('ms-autosize-textarea textarea, ms-prompt-box textarea, textarea, div[contenteditable="true"]'));
        const chatInputs = allTextareas.filter(el => {
            if (!el || el.disabled || el.readOnly) return false;
            if (el.closest('ms-system-instructions, .system-instructions, ms-prompt-header, header')) return false;
            const aria = ((el.getAttribute('aria-label') || '') + ' ' + (el.getAttribute('placeholder') || '')).toLowerCase();
            if (aria.includes('system') || aria.includes('instruction') || aria.includes('系统') || aria.includes('title') || aria.includes('untitled')) {
                return false;
            }
            return true;
        });

        if (chatInputs.length > 0) {
            return chatInputs[chatInputs.length - 1];
        }
        return null;
    }

    function setAngularNativeValue(element, value) {
        if (!element) return;
        try { element.focus(); } catch (e) {}

        let assigned = false;
        if (element.tagName && (element.tagName.toLowerCase() === 'textarea' || element.tagName.toLowerCase() === 'input')) {
            const candidateProtos = [
                Object.getPrototypeOf(element),
                window.HTMLTextAreaElement && window.HTMLTextAreaElement.prototype
            ];
            for (const proto of candidateProtos) {
                if (!proto) continue;
                try {
                    const setter = Object.getOwnPropertyDescriptor(proto, 'value')?.set;
                    if (setter) {
                        setter.call(element, value);
                        assigned = true;
                        break;
                    }
                } catch (e) {}
            }
            if (!assigned) {
                try { element.value = value; } catch (e) {}
            }
        } else if (element.isContentEditable) {
            try { element.textContent = value; } catch (e) {}
        }

        try { element.dispatchEvent(new Event('input', { bubbles: true, composed: true })); } catch (e) {}
        try { element.dispatchEvent(new InputEvent('input', { bubbles: true, composed: true, inputType: 'insertText', data: value })); } catch (e) {}
        try { element.dispatchEvent(new Event('change', { bubbles: true, composed: true })); } catch (e) {}
    }

function dispatchPhysicalClick(el) {
        if (!el) return;
        try {
            el.disabled = false;
            el.removeAttribute('disabled');
            el.removeAttribute('aria-disabled');
            el.classList.remove('mat-mdc-button-disabled');
        } catch (e) {}

        try {
            const rect = el.getBoundingClientRect();
            const clientX = (rect && rect.width > 0) ? rect.left + rect.width / 2 : 10;
            const clientY = (rect && rect.height > 0) ? rect.top + rect.height / 2 : 10;
            const win = (typeof unsafeWindow !== 'undefined') ? unsafeWindow : window;
            const PEvent = win.PointerEvent || PointerEvent;
            const MEvent = win.MouseEvent || MouseEvent;

            const commonInit = {
                bubbles: true,
                cancelable: true,
                composed: true,
                view: win,
                detail: 1,
                screenX: clientX,
                screenY: clientY,
                clientX: clientX,
                clientY: clientY,
                button: 0,
                buttons: 1,
                which: 1
            };

            // 1. 尝试聚焦目标元素
            try { el.focus(); } catch (e) {}

            // 2. 指针下压 (pointerdown)
            if (typeof PEvent === 'function') {
                try {
                    el.dispatchEvent(new PEvent('pointerdown', {
                        ...commonInit,
                        pointerId: 1,
                        pointerType: 'mouse',
                        isPrimary: true
                    }));
                } catch (e) {}
            }

            // 3. 鼠标下压 (mousedown)
            try {
                el.dispatchEvent(new MEvent('mousedown', commonInit));
            } catch (e) {}

            // 4. 指针抬起 (pointerup)
            if (typeof PEvent === 'function') {
                try {
                    el.dispatchEvent(new PEvent('pointerup', {
                        ...commonInit,
                        pointerId: 1,
                        pointerType: 'mouse',
                        isPrimary: true,
                        buttons: 0
                    }));
                } catch (e) {}
            }

            // 5. 鼠标抬起 (mouseup)
            try {
                el.dispatchEvent(new MEvent('mouseup', {
                    ...commonInit,
                    buttons: 0
                }));
            } catch (e) {}

            // 6. 单一确定性物理点击（优先原生 el.click()，若不支持则回退派发单次标准 click，杜绝两者叠加双重 Click 踩踏）
            if (typeof el.click === 'function') {
                el.click();
            } else {
                try {
                    el.dispatchEvent(new MEvent('click', {
                        ...commonInit,
                        buttons: 0
                    }));
                } catch (e) {}
            }
        } catch (e) {
            console.error('[AFL_BRIDGE] dispatchPhysicalClick error:', e);
            try { if (typeof el.click === 'function') el.click(); } catch (err) {}
        }
    }

    let activeIgnitionTimer = null;

    function triggerRun(inputEl) {
        lastAttemptTimestamp = Date.now();
        const activeInput = inputEl || findInputTextarea();

        // 判定 1：统帅是否已进入生成态（若已生成则绝不二次点击，防范误触 Stop 或二次触发打断）
        if (checkAiStudioGenerating() || isGenerating || generationPhase === 'PHASE1_GENERATING') {
            return false;
        }

        // 唤醒输入框与 Angular 脏检查与 Token 计算
        try {
            if (activeInput) {
                activeInput.focus();
                activeInput.dispatchEvent(new Event('input', { bubbles: true, composed: true }));
                activeInput.dispatchEvent(new Event('change', { bubbles: true, composed: true }));
            }
        } catch (e) {}

        const initialText = activeInput ? (activeInput.value || activeInput.textContent || '').trim() : '';

        if (activeIgnitionTimer) {
            clearInterval(activeIgnitionTimer);
            activeIgnitionTimer = null;
        }

        const ignitionStartTs = Date.now();
        let lastClickTs = 0;
        let hasFiredClick = false;

        const attemptIgnite = () => {
            const elapsedMs = Date.now() - ignitionStartTs;

            // 成功退出条件 1：检测到统帅已进入生成态，或按钮已变为 Stop 状态
            const runBtn = findRunButton();
            if (checkAiStudioGenerating() || (runBtn && isRunButtonInStopState(runBtn))) {
                console.log(`[AFL_BRIDGE] 🚀 点火成功！检测到统帅已进入生成态 (耗时: ${elapsedMs}ms)`);
                if (activeIgnitionTimer) {
                    clearInterval(activeIgnitionTimer);
                    activeIgnitionTimer = null;
                }
                generationPhase = 'PHASE1_GENERATING';
                isGenerating = true;
                quietCountdownStart = 0;
                isScriptInjecting = false;
                updateHUDStatus();
                return;
            }

            // 成功退出条件 2：输入框文本已被 AI Studio 消费清空
            const curInput = activeInput || findInputTextarea();
            if (curInput && initialText.length > 0) {
                const curVal = (curInput.value || curInput.textContent || '').trim();
                if (curVal.length === 0) {
                    console.log(`[AFL_BRIDGE] 🚀 点火成功！输入框文本已被系统消费清空 (耗时: ${elapsedMs}ms)`);
                    if (activeIgnitionTimer) {
                        clearInterval(activeIgnitionTimer);
                        activeIgnitionTimer = null;
                    }
                    generationPhase = 'PHASE1_GENERATING';
                    isGenerating = true;
                    quietCountdownStart = 0;
                    isScriptInjecting = false;
                    updateHUDStatus();
                    return;
                }
            }

            // 熔断保护：4000ms 超时退出
            if (elapsedMs >= 4000) {
                console.warn(`[AFL_BRIDGE] ⚠️ 点火轮询超时 (4000ms)，退出点火循环`);
                if (activeIgnitionTimer) {
                    clearInterval(activeIgnitionTimer);
                    activeIgnitionTimer = null;
                }
                isScriptInjecting = false;
                return;
            }

            // 解禁状态判定与单枪击发 / 防抖流控（防暴力连点，点击飞行期互斥锁至少 1800ms）
            const unlocked = isRunButtonUnlocked();
            const canClickNow = !hasFiredClick || (Date.now() - lastClickTs) >= 1800;

            if ((unlocked || elapsedMs >= 300) && canClickNow) {
                if (!unlocked && elapsedMs >= 300 && runBtn) {
                    console.log(`[AFL_BRIDGE] ⚡ [300ms 兜底] 强行撬锁 Run 按钮 (剥离 disabled 属性)...`);
                    unlockRunButton(runBtn);
                }

                if (runBtn) {
                    console.log(`[AFL_BRIDGE] ⚡ 叩击 Run 按钮 (耗时: ${elapsedMs}ms, 自然解禁: ${unlocked})...`);
                    hasFiredClick = true;
                    lastClickTs = Date.now();
                    lastAttemptTimestamp = Date.now();
                    dispatchPhysicalClick(runBtn);
                }
            } else if (!unlocked && !hasFiredClick) {
                // 尚未解禁且未击发（处于 0ms~300ms Angular 计算窗口），向 input 持续派发 input 事件唤醒脏检查
                try {
                    if (curInput) {
                        curInput.dispatchEvent(new Event('input', { bubbles: true, composed: true }));
                    }
                } catch (e) {}
            }
        };

        // 立即执行第 0ms 首次探测
        attemptIgnite();

        // 若首次未能立即进入生成态，启动 50ms 轮询
        if (!checkAiStudioGenerating() && !(findRunButton() && isRunButtonInStopState(findRunButton()))) {
            activeIgnitionTimer = setInterval(attemptIgnite, 50);
        }
        return true;
    }
    function executeInPageRetry() {
        if (checkAiStudioGenerating() || getLatestModelResponseText().trim().length >= 20) {
            return false;
        }

        isScriptInjecting = true;
        setTimeout(() => { isScriptInjecting = false; }, 1200);

        const turns = Array.from(document.querySelectorAll('ms-chat-turn'));
        const recentTurns = turns.slice(-2).reverse();
        for (const turn of recentTurns) {
            const btns = Array.from(turn.querySelectorAll('button, [role="button"]'));
            const rerunBtn = btns.find(b => {
                if (b.disabled || !isElementVisible(b)) return false;
                const aria = (b.getAttribute('aria-label') || '').toLowerCase();
                const tooltip = (b.getAttribute('mattooltip') || b.getAttribute('title') || '').toLowerCase();
                const txt = (b.textContent || '').toLowerCase();
                const iconTxt = (b.querySelector('mat-icon, .material-symbols-outlined')?.textContent || '').trim().toLowerCase();
                return aria.includes('rerun') || aria.includes('retry') || aria.includes('regenerate') ||
                       tooltip.includes('rerun') || tooltip.includes('retry') ||
                       txt.includes('rerun') || txt.includes('retry') || txt.includes('try again') ||
                       iconTxt === 'refresh' || iconTxt === 'replay' || iconTxt === 'autorenew';
            });
            if (rerunBtn) {
                lastAttemptTimestamp = Date.now();
                dispatchPhysicalClick(rerunBtn);
                return true;
            }
        }

        const inputEl = findInputTextarea();
        if (inputEl) {
            const currentInputVal = (inputEl.value || inputEl.textContent || '').trim();
            if (currentInputVal.length > 10) {
                return triggerRun(inputEl);
            }
        }
        return false;
    }

    // -------------------------------------------------------------
    // 7. 单回合生成态探测与正文提取
    // -------------------------------------------------------------
    function checkAiStudioGenerating() {
        const latestTxt = getLatestModelResponseText();
        if (hasTrailingEofBeacon(latestTxt)) {
            const cleanedForHash = latestTxt.replace(EOF_STRIP_REGEX, '').trim();
            if (simpleHash(cleanedForHash) !== getDispatchedHash()) {
                return false;
            }
        }

        const runBtn = findRunButton();
        if (isRunButtonInStopState(runBtn)) {
            return true;
        }

        if (generationPhase !== 'PHASE_UPLOADING_FILES') {
            const turns = document.querySelectorAll('ms-chat-turn');
            if (turns.length > 0) {
                const lastTurn = turns[turns.length - 1];
                const spinners = Array.from(
                    lastTurn.querySelectorAll('mat-progress-bar, mat-spinner, mat-progress-spinner, .spinner, .loading')
                );
                if (spinners.some(isElementVisible)) {
                    return true;
                }
            }
        }
        return false;
    }

    function detectAiStudioErrorState() {
        if (generationPhase === 'PHASE_UPLOADING_FILES' || checkAiStudioGenerating()) return null;
        if (Date.now() - lastAttemptTimestamp < FLIGHT_GRACE_PERIOD_MS) return null;

        const latestModelText = getLatestModelResponseText().trim();
        const errorRegex = /(an internal error has occurred|an error occurred|failed to generate|something went wrong|resource has been exhausted|request timed out|deadline exceeded|network error|failed to fetch|disconnected|unable to complete|please try again|you've reached your rate limit|rate limit)/i;
        if (latestModelText.length > 0 && errorRegex.test(latestModelText)) {
            return `ModelErrorText: ${latestModelText.slice(0, 100)}`;
        }
        if (latestModelText.length >= 20) return null;

        const turns = Array.from(document.querySelectorAll('ms-chat-turn'));
        if (turns.length > 0) {
            const lastTurn = turns[turns.length - 1];
            const errSelectors = '.error-container, .error-message, ms-error-message, .model-error, mat-error';
            const errEl = lastTurn.querySelector(errSelectors);
            if (errEl && isElementVisible(errEl)) {
                const errTxt = (errEl.textContent || '').trim();
                if (errTxt.length > 0) return `TurnErrorDOM: ${errTxt.slice(0, 100)}`;
            }

            const icons = Array.from(lastTurn.querySelectorAll('mat-icon, .material-symbols-outlined')).filter(isElementVisible);
            for (const ic of icons) {
                const iconName = (ic.textContent || '').trim().toLowerCase();
                if (iconName === 'error' || iconName === 'error_outline' || iconName === 'warning') {
                    const turnTxt = (lastTurn.textContent || '').trim();
                    return `TurnErrorIcon: ${turnTxt.slice(0, 100)}`;
                }
            }

            if (lastTurn.querySelector('.chat-turn-container.model')) {
                const rawTurnTxt = (lastTurn.textContent || '').trim();
                if (rawTurnTxt.length < 300 && errorRegex.test(rawTurnTxt)) {
                    return `ModelTurnErrorText: ${rawTurnTxt.slice(0, 100)}`;
                }
            }
        }

        const alerts = Array.from(document.querySelectorAll('mat-snack-bar-container, [role="alert"], .mat-mdc-snack-bar-label')).filter(isElementVisible);
        for (const al of alerts) {
            const alTxt = (al.textContent || '').trim();
            if (errorRegex.test(alTxt)) return `AlertToastError: ${alTxt.slice(0, 100)}`;
        }
        return null;
    }

    function cleanModelDecisionText(rawText) {
        if (!rawText) return '';
        let text = rawText.trim();
        text = text.replace(/<(?:thought|thinking)>[\s\S]*?<\/(?:thought|thinking)>/gi, '').trim();
        text = text.replace(/\[(?:thought|thinking)\][\s\S]*?\[\/(?:thought|thinking)\]/gi, '').trim();
        text = text.replace(/```(?:thought|thinking)[\s\S]*?```/gi, '').trim();
        text = text.replace(/^(?:Thinking Process|Thought Process|Thinking):\s*[\s\S]*?(?=\n\n(?:[#A-Z0-9\u4e00-\u9fa5]|---)|$)/i, '').trim();
        return text;
    }

    function isLatestTurnCompletedModelReply() {
        const turns = Array.from(document.querySelectorAll('ms-chat-turn:not(.thought-activity-host)')).filter(
            el => !el.closest('thought-activity-host') && !el.classList.contains('thought-activity-host')
        );
        if (turns.length === 0) return true;
        const lastTurn = turns[turns.length - 1];
        const hasUser = lastTurn.querySelector('.chat-turn-container.user, .user-prompt-container') !== null;
        const hasModel = lastTurn.querySelector('.chat-turn-container.model, .model-prompt-container') !== null;
        if (hasUser && !hasModel) return false;
        return true;
    }

    function isLatestTurnFromAutomatedCapsule() {
        const userContainers = Array.from(
            document.querySelectorAll('ms-chat-turn .chat-turn-container.user, .user-prompt-container')
        );
        if (userContainers.length > 0) {
            const latestUserEl = userContainers[userContainers.length - 1];
            const latestUserText = (latestUserEl.textContent || '').trim();
            if (latestUserText.length > 0) {
                if (hasCapsuleSignature(latestUserText)) return true;
            }
        }

        if (sessionStorage.getItem('AFL_LAST_RUN_ORIGIN') === 'MANUAL_HUMAN') {
            const activeTicket = sessionStorage.getItem('AFL_ACTIVE_TICKET') || (cachedAwaitingTicket && cachedAwaitingTicket.id);
            if (activeTicket) {
                sessionStorage.setItem('AFL_LAST_RUN_ORIGIN', 'AUTOMATED_CAPSULE');
                return true;
            }
            return false;
        }

        const activeTicket = sessionStorage.getItem('AFL_ACTIVE_TICKET') || (cachedAwaitingTicket && cachedAwaitingTicket.id);
        if (activeTicket && sessionStorage.getItem('AFL_LAST_RUN_ORIGIN') === 'AUTOMATED_CAPSULE') {
            return true;
        }
        return sessionStorage.getItem('AFL_LAST_RUN_ORIGIN') === 'AUTOMATED_CAPSULE';
    }

    function getModelTurnCount() {
        return document.querySelectorAll("ms-chat-turn:not(.thought-activity-host) .chat-turn-container.model, .chat-turn-container.model").length;
    }

    function getLatestModelResponseText() {
        if (!isLatestTurnCompletedModelReply()) return '';

        const modelContainers = Array.from(
            document.querySelectorAll("ms-chat-turn:not(.thought-activity-host) .chat-turn-container.model, .chat-turn-container.model")
        ).filter(el => !el.closest(".thought-activity-host") && !el.closest("thought-activity-host") && !el.classList.contains("thought-activity-host"));

        if (modelContainers.length === 0) return '';

        const userContainers = Array.from(
            document.querySelectorAll("ms-chat-turn .chat-turn-container.user, .user-prompt-container")
        );
        const lastUser = userContainers.length > 0 ? userContainers[userContainers.length - 1] : null;

        // 收集在最后一个 User Prompt 之后生成的所有 Model 容器（对抗 Interleaved Thinking 碎裂成多个 Turn）
        const targetModelContainers = lastUser
            ? modelContainers.filter(mc => (lastUser.compareDocumentPosition(mc) & Node.DOCUMENT_POSITION_FOLLOWING) !== 0)
            : [modelContainers[modelContainers.length - 1]];

        const effectiveContainers = targetModelContainers.length > 0 ? targetModelContainers : [modelContainers[modelContainers.length - 1]];

        const gatheredChunks = [];

        for (const container of effectiveContainers) {
            try {
                const clone = container.cloneNode(true);
                clone.querySelectorAll(
                    "thought-activity-host, .thought-activity-host, ms-thought-chunk, .thought-container, " +
                    ".thought-wrapper, mat-expansion-panel, .thinking-content, [aria-label*='thought' i], " +
                    "[aria-label*='thinking' i], .error-container, .error-message, button, mat-icon, style, script"
                ).forEach(e => e.remove());

                const textChunks = Array.from(clone.querySelectorAll("ms-text-chunk, ms-code-chunk"));
                const targetEls = textChunks.length > 0 ? textChunks : Array.from(clone.querySelectorAll(".turn-content"));
                if (targetEls.length > 0) {
                    const txt = targetEls.map(el => (el.textContent || "").trim()).filter(Boolean).join("\n\n");
                    if (txt.length > 0) gatheredChunks.push(txt);
                } else {
                    const fallbackTxt = (clone.textContent || "").trim();
                    if (fallbackTxt.length > 0) gatheredChunks.push(fallbackTxt);
                }
            } catch (e) {}
        }

        const rawText = gatheredChunks.join("\n\n");
        return cleanModelDecisionText(rawText);
    }

    function finalizeAndDispatchReply(latestText, isManualForce = false) {
        const cleanText = latestText.replace(EOF_STRIP_REGEX, '').trim();
        const textHash = simpleHash(cleanText);
        const lastDispatched = getDispatchedHash();

        if (!isManualForce && textHash === lastDispatched) return;
        if (cleanText.length <= 20) return;

        if (!isManualForce && !isLatestTurnFromAutomatedCapsule()) {
            if (generationPhase !== 'PHASE_HUMAN_CHAT_BYPASS') {
                generationPhase = 'PHASE_HUMAN_CHAT_BYPASS';
                updateHUDStatus();
            }
            return;
        }

        const baselineCount = parseInt(sessionStorage.getItem('AFL_BASELINE_MODEL_COUNT') || '0', 10);
        if (!isManualForce && baselineCount > 0 && getModelTurnCount() < baselineCount + 1) {
            return;
        }

        if (cachedAwaitingTicket && cachedAwaitingTicket.prompt_snippet && cleanText.startsWith(cachedAwaitingTicket.prompt_snippet.slice(0, 40))) {
            return;
        }

        let activeTicket = '';
        try {
            activeTicket = sessionStorage.getItem('AFL_ACTIVE_TICKET') || (cachedAwaitingTicket && cachedAwaitingTicket.id) || '';
            setDispatchedHash(textHash);
            sessionStorage.removeItem('AFL_AWAITING_REPLY');
            sessionStorage.removeItem('AFL_ACTIVE_TICKET');
            sessionStorage.removeItem('AFL_ACTIVE_PROMPT_SNIPPET');
            sessionStorage.removeItem('AFL_BASELINE_MODEL_COUNT');
        } catch (e) {}

        cachedAwaitingTicket = null;
        generationPhase = 'IDLE';
        isGenerating = false;
        autoIterationCount++;

        const countEl = document.getElementById('afl-round-count');
        if (countEl) countEl.textContent = `轮次: ${autoIterationCount}`;
        updateHUDStatus();

        const currentTitle = getPromptTitle();
        console.log(`[AFL_BRIDGE] 🚀 Dispatching Argon's reply (${cleanText.length} chars, ticket: ${activeTicket}) from [${currentTitle}]...`);
        GM_xmlhttpRequest({
            method: 'POST',
            url: `${BRIDGE_HOST}/api/bridge/dispatch`,
            headers: { 'Content-Type': 'application/json' },
            data: JSON.stringify({
                ticket_id: activeTicket,
                raw_text: cleanText,
                source_title: currentTitle,
                source_url: window.location.href
            }),
            onload: () => console.log('[AFL_BRIDGE] Successfully dispatched reply to bridge.'),
            onerror: (err) => console.error('[AFL_BRIDGE] Failed to dispatch to bridge:', err)
        });
    }

    // -------------------------------------------------------------
    // 8. 核心扫描与派发主循环
    // -------------------------------------------------------------
    function scanForNewModelReplies() {
        if (!isBridgeActive || !isCommanderTab()) return;
        if (generationPhase === 'PHASE_UPLOADING_FILES') return;

        if (sessionStorage.getItem('AFL_LAST_RUN_ORIGIN') === 'MANUAL_HUMAN') {
            const activeTicket = sessionStorage.getItem('AFL_ACTIVE_TICKET') || (cachedAwaitingTicket && cachedAwaitingTicket.id);
            if (!activeTicket) {
                if (generationPhase !== 'PHASE_HUMAN_CHAT_BYPASS') {
                    generationPhase = 'PHASE_HUMAN_CHAT_BYPASS';
                    updateHUDStatus();
                }
                return;
            } else {
                sessionStorage.setItem('AFL_LAST_RUN_ORIGIN', 'AUTOMATED_CAPSULE');
            }
        }

        const awaiting = sessionStorage.getItem('AFL_AWAITING_REPLY') === 'true';
        if (!awaiting && generationPhase === 'IDLE') return;

        const currentText = getLatestModelResponseText().trim();
        const cleanedForHash = currentText.replace(EOF_STRIP_REGEX, '').trim();
        const lastDispatched = getDispatchedHash();

        const isErrorText = /(?:an internal error has occurred|an error occurred|failed to generate|something went wrong|resource has been exhausted|request timed out|deadline exceeded|network error|failed to fetch|disconnected|unable to complete|please try again|you've reached your rate limit|rate limit)/i.test(cleanedForHash);
        if (isErrorText) {
            return;
        }

        if (cleanedForHash.length >= 20 && simpleHash(cleanedForHash) !== lastDispatched && hasTrailingEofBeacon(currentText)) {
            if (isLatestTurnFromAutomatedCapsule()) {
                finalizeAndDispatchReply(currentText);
                return;
            }
        }

        const activeTicket = sessionStorage.getItem('AFL_ACTIVE_TICKET') || (cachedAwaitingTicket && cachedAwaitingTicket.id) || 'default_ticket';
        const isBusy = checkAiStudioGenerating();

        if (isBusy) {
            if (generationPhase !== 'PHASE1_GENERATING') {
                generationPhase = 'PHASE1_GENERATING';
                isGenerating = true;
                retryBackoffStart = 0;
                updateHUDStatus();
            }
            quietCountdownStart = 0;
            lastObservedResponseText = currentText;
            return;
        }

        if (cleanedForHash.length >= 20 && simpleHash(cleanedForHash) !== lastDispatched) {
            if (!isLatestTurnFromAutomatedCapsule()) {
                if (generationPhase !== 'PHASE_HUMAN_CHAT_BYPASS') {
                    generationPhase = 'PHASE_HUMAN_CHAT_BYPASS';
                    updateHUDStatus();
                }
                return;
            }

            if (generationPhase !== 'PHASE2_QUIET_COUNTDOWN') {
                generationPhase = 'PHASE2_QUIET_COUNTDOWN';
                quietCountdownStart = Date.now();
                lastObservedResponseText = currentText;
                updateHUDStatus();
                return;
            }

            if (currentText !== lastObservedResponseText) {
                lastObservedResponseText = currentText;
                quietCountdownStart = Date.now();
                return;
            }

            if (Date.now() - quietCountdownStart >= QUIET_COUNTDOWN_DURATION_MS) {
                finalizeAndDispatchReply(currentText);
            }
            return;
        }

        if (!navigator.onLine) return;

        const detectedError = detectAiStudioErrorState();
        if (detectedError && isLatestTurnFromAutomatedCapsule()) {
            const currentRetries = getRetryCount(activeTicket);

            if (currentRetries >= MAX_AUTO_RETRIES) {
                if (generationPhase !== 'PHASE_MANUAL_AWAITED') {
                    generationPhase = 'PHASE_MANUAL_AWAITED';
                    updateHUDStatus();
                    reportStatusToBridge('RETRY_EXHAUSTED_AWAITING_MANUAL', {
                        retry_count: currentRetries,
                        error: detectedError
                    });
                }
                return;
            }

            if (generationPhase !== 'PHASE_RETRY_BACKOFF') {
                generationPhase = 'PHASE_RETRY_BACKOFF';
                retryBackoffStart = Date.now();
                return;
            }

            if (Date.now() - retryBackoffStart >= RETRY_BACKOFF_DELAY_MS) {
                const nextRetry = currentRetries + 1;
                setRetryCount(activeTicket, nextRetry);
                retryBackoffStart = 0;
                reportStatusToBridge('AUTO_RETRY_TRIGGERED', {
                    retry_attempt: nextRetry,
                    max_retries: MAX_AUTO_RETRIES,
                    error: detectedError
                });

                const triggered = executeInPageRetry();
                generationPhase = triggered ? 'PHASE1_GENERATING' : 'PHASE_MANUAL_AWAITED';
                updateHUDStatus();
            }
        }
    }

    // -------------------------------------------------------------
    // 9. 胶囊注入与防遮挡轮询
    // -------------------------------------------------------------
    function finalizeTextAndFireRun(finalConsultText, consultId, currentTitle) {
        const inputArea = findInputTextarea();
        let valueUpdated = false;
        if (inputArea) {
            const currentVal = (inputArea.value || inputArea.textContent || '').trim();
            if (currentVal !== finalConsultText.trim()) {
                setAngularNativeValue(inputArea, finalConsultText);
                valueUpdated = true;
            }
        }

        const doFire = () => {
            const targetInput = inputArea || findInputTextarea();
            triggerRun(targetInput);
            lastAttemptTimestamp = Date.now();

            GM_xmlhttpRequest({
                method: 'POST',
                url: `${BRIDGE_HOST}/api/bridge/ack_consultation`,
                headers: { 'Content-Type': 'application/json' },
                data: JSON.stringify({ status: 'delivered', id: consultId, target_title: currentTitle })
            });

            setTimeout(() => {
                if (checkAiStudioGenerating()) {
                    generationPhase = 'PHASE1_GENERATING';
                    isGenerating = true;
                    quietCountdownStart = 0;
                    updateHUDStatus();
                }
            }, 300);
            setTimeout(() => { isTaskInjecting = false; }, 3500);
        };

        if (valueUpdated) {
            // 显式加入 80ms~100ms 宏任务等待窗，让 Angular 内部状态树与 Token 估算器从容完成词元绑定并移除 disabled
            setTimeout(doFire, 100);
        } else {
            doFire();
        }
    }

    function injectConsultationAndRun(consultText, consultId, attachments = []) {
        if (!isBridgeActive || !isCommanderTab()) return;

        const currentTitle = getPromptTitle();
        const inputArea = findInputTextarea();
        if (!inputArea) return;

        isTaskInjecting = true;

        const existingModelText = getLatestModelResponseText().replace(EOF_STRIP_REGEX, '').trim();
        if (existingModelText.length > 20) {
            setDispatchedHash(simpleHash(existingModelText));
        }

        isScriptInjecting = true;
        try {
            sessionStorage.setItem('AFL_BASELINE_MODEL_COUNT', String(getModelTurnCount()));
            sessionStorage.setItem('AFL_LAST_RUN_ORIGIN', 'AUTOMATED_CAPSULE');
            sessionStorage.setItem('AFL_AWAITING_REPLY', 'true');
            sessionStorage.setItem('AFL_ACTIVE_PROMPT_SNIPPET', consultText.trim().slice(0, 60));
            if (consultId) {
                sessionStorage.setItem('AFL_ACTIVE_TICKET', consultId);
                setRetryCount(consultId, 0);
            }
        } catch (e) {}

        if (!attachments || attachments.length === 0) {
            setAngularNativeValue(inputArea, consultText);
            // 显式预留 100ms 宏任务等待窗，让 Angular 表单与 Token 估算器从容完成词元绑定并移除 disabled
            setTimeout(() => {
                finalizeTextAndFireRun(consultText, consultId, currentTitle);
            }, 100);
            return;
        }

        generationPhase = 'PHASE_UPLOADING_FILES';
        updateHUDStatus();

        const fileNames = attachments.map(a => a.name);
        reportStatusToBridge('ATTACHMENT_INJECTING', { count: attachments.length, files: fileNames });

        let fileObjects = [];
        try {
            fileObjects = attachments.map(convertAttachmentToFile);
        } catch (err) {
            const fallbackText = buildInlineFallbackText(attachments, consultText);
            reportStatusToBridge('ATTACHMENT_FALLBACK_INLINE', { reason: 'base64_decode_error' });
            setAngularNativeValue(inputArea, fallbackText);
            setTimeout(() => {
                finalizeTextAndFireRun(fallbackText, consultId, currentTitle);
            }, 100);
            return;
        }

        injectFilesCascading(fileObjects, (injectResult) => {
            if (!injectResult.mounted) {
                const fallbackText = buildInlineFallbackText(attachments, consultText);
                reportStatusToBridge('ATTACHMENT_FALLBACK_INLINE', { reason: 'dom_chip_not_mounted' });
                setAngularNativeValue(findInputTextarea(), fallbackText);
                setTimeout(() => {
                    finalizeTextAndFireRun(fallbackText, consultId, currentTitle);
                }, 100);
                return;
            }

            const curInput = findInputTextarea();
            if (curInput) setAngularNativeValue(curInput, consultText);

            const uploadStartTs = Date.now();
            let stableReadySince = 0;
            let lastTelemetrySec = 0;

            const uploadTimer = setInterval(() => {
                if (generationPhase !== 'PHASE_UPLOADING_FILES') {
                    clearInterval(uploadTimer);
                    return;
                }
                const elapsedMs = Date.now() - uploadStartTs;
                const elapsedSec = Math.floor(elapsedMs / 1000);

                const uploadErr = detectAttachmentUploadError();
                if (uploadErr) {
                    clearInterval(uploadTimer);
                    const fallbackText = buildInlineFallbackText(attachments, consultText);
                    reportStatusToBridge('ATTACHMENT_FALLBACK_INLINE', { reason: uploadErr });
                    setAngularNativeValue(findInputTextarea(), fallbackText);
                    setTimeout(() => {
                        finalizeTextAndFireRun(fallbackText, consultId, currentTitle);
                    }, 100);
                    return;
                }

                const stillUploading = isComposerStillUploadingFiles();
                const runUnlocked = isRunButtonUnlocked();

                if (!stillUploading && runUnlocked) {
                    if (stableReadySince === 0) {
                        stableReadySince = Date.now();
                    } else if (Date.now() - stableReadySince >= 600) {
                        clearInterval(uploadTimer);
                        reportStatusToBridge('ATTACHMENT_READY_AND_RUN', {
                            method: injectResult.method,
                            elapsed_ms: elapsedMs,
                            chip_count: countComposerFileChips()
                        });
                        finalizeTextAndFireRun(consultText, consultId, currentTitle);
                        return;
                    }
                } else {
                    stableReadySince = 0;
                    if (elapsedSec >= 3 && elapsedSec - lastTelemetrySec >= 5) {
                        lastTelemetrySec = elapsedSec;
                        reportStatusToBridge('ATTACHMENT_UPLOADING', { elapsed_sec: elapsedSec });
                    }
                }

                if (elapsedMs >= MAX_FILE_UPLOAD_WAIT_MS) {
                    clearInterval(uploadTimer);
                    const fallbackText = buildInlineFallbackText(attachments, consultText);
                    reportStatusToBridge('ATTACHMENT_FALLBACK_INLINE', { reason: 'upload_timeout_90s' });
                    setAngularNativeValue(findInputTextarea(), fallbackText);
                    setTimeout(() => {
                        finalizeTextAndFireRun(fallbackText, consultId, currentTitle);
                    }, 100);
                }
            }, 250);
        });
    }

    function pollForConsultations() {
        if (!isBridgeActive || !isCommanderTab()) return;
        if (generationPhase === 'PHASE_UPLOADING_FILES' || checkAiStudioGenerating() || isGenerating || isTaskInjecting) return;

        const currentTitle = getPromptTitle();
        GM_xmlhttpRequest({
            method: 'GET',
            url: `${BRIDGE_HOST}/api/bridge/poll_consultation?title=${encodeURIComponent(currentTitle)}`,
            onload: (res) => {
                try {
                    const data = JSON.parse(res.responseText);
                    if (data.status === 'has_consultation' && data.consultation) {
                        const consult = data.consultation;
                        if (!consult.id) return;
                        if (dispatchedTicketIds.has(consult.id) || sessionStorage.getItem('AFL_ACTIVE_TICKET') === consult.id || isTaskInjecting) {
                            console.log(`[AFL_BRIDGE] ⚠️ 拦截重复 Ticket 派发尝试: [${consult.id}] 正在注入或已在执行列表中！`);
                            return;
                        }
                        dispatchedTicketIds.add(consult.id);
                        cachedAwaitingTicket = consult;
                        if (consult.consult_text) {
                            injectConsultationAndRun(consult.consult_text, consult.id, consult.attachments || []);
                        }
                        return;
                    }

                    if (data.awaiting_ticket && data.awaiting_ticket.id) {
                        cachedAwaitingTicket = data.awaiting_ticket;
                        const currentActive = sessionStorage.getItem('AFL_ACTIVE_TICKET');
                        if (currentActive !== data.awaiting_ticket.id) {
                            sessionStorage.setItem('AFL_ACTIVE_TICKET', data.awaiting_ticket.id);
                            sessionStorage.setItem('AFL_AWAITING_REPLY', 'true');
                            if (data.awaiting_ticket.prompt_snippet) {
                                sessionStorage.setItem('AFL_ACTIVE_PROMPT_SNIPPET', data.awaiting_ticket.prompt_snippet);
                            }
                            if (!sessionStorage.getItem('AFL_LAST_RUN_ORIGIN')) {
                                sessionStorage.setItem('AFL_LAST_RUN_ORIGIN', 'AUTOMATED_CAPSULE');
                            }
                            updateHUDStatus();
                        }
                    }
                } catch (e) {}
            }
        });
    }

    function sendHeartbeat() {
        const currentTitle = getPromptTitle();
        GM_xmlhttpRequest({
            method: 'POST',
            url: `${BRIDGE_HOST}/api/bridge/heartbeat`,
            headers: { 'Content-Type': 'application/json' },
            data: JSON.stringify({
                version: '6.0.7',
                title: currentTitle,
                url: window.location.href,
                is_active: isBridgeActive,
                is_commander: isCommanderTab(),
                phase: generationPhase,
                active_ticket: sessionStorage.getItem('AFL_ACTIVE_TICKET') || '',
                timestamp: Date.now()
            }),
            onload: (res) => {
                try {
                    const data = JSON.parse(res.responseText);
                    if (data.awaiting_ticket && data.awaiting_ticket.id) {
                        cachedAwaitingTicket = data.awaiting_ticket;
                        sessionStorage.setItem('AFL_LAST_RUN_ORIGIN', 'AUTOMATED_CAPSULE');
                        if (sessionStorage.getItem('AFL_AWAITING_REPLY') !== 'true') {
                            sessionStorage.setItem('AFL_ACTIVE_TICKET', data.awaiting_ticket.id);
                            sessionStorage.setItem('AFL_AWAITING_REPLY', 'true');
                            if (data.awaiting_ticket.prompt_snippet) {
                                sessionStorage.setItem('AFL_ACTIVE_PROMPT_SNIPPET', data.awaiting_ticket.prompt_snippet);
                            }
                            updateHUDStatus();
                        }
                    }
                } catch (e) {}
            }
        });
    }

    // -------------------------------------------------------------
    // 10. 防遮挡后台扩展 IPC 轮询驱动器
    // -------------------------------------------------------------
    function onTick() {
        if (!document.body) return;
        const now = Date.now();
        try { scanForNewModelReplies(); } catch (e) {}

        if (now - lastPollTs >= 1000) {
            lastPollTs = now;
            try { pollForConsultations(); } catch (e) {}
        }
        if (now - lastHudTs >= 1500) {
            lastHudTs = now;
            try { createFloatingHUD(); } catch (e) {}
        }
        if (now - lastHeartbeatTs >= 2500) {
            lastHeartbeatTs = now;
            try { sendHeartbeat(); } catch (e) {}
        }
    }

    function triggerAntiOcclusionPulse() {
        if (isIpcPulseInFlight) return;
        isIpcPulseInFlight = true;

        const next = (delayMs) => {
            isIpcPulseInFlight = false;
            onTick();
            setTimeout(triggerAntiOcclusionPulse, delayMs);
        };

        GM_xmlhttpRequest({
            method: 'GET',
            url: `${BRIDGE_HOST}/api/status?wait_ms=120&_t=${Date.now()}`,
            timeout: 1500,
            onload: () => next(80),
            onerror: () => next(300),
            ontimeout: () => next(150)
        });
    }

    initAntiOcclusionLock();
    initManualInputInterception();
    triggerAntiOcclusionPulse();

    setTimeout(() => {
        const awaiting = sessionStorage.getItem('AFL_AWAITING_REPLY') === 'true';
        const existingDispatched = getDispatchedHash();
        if (!awaiting && !existingDispatched && !cachedAwaitingTicket) {
            const initialText = getLatestModelResponseText().replace(EOF_STRIP_REGEX, '').trim();
            if (initialText.length > 20) {
                setDispatchedHash(simpleHash(initialText));
            }
        }
    }, 1500);

})();
