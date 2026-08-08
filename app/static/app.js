const state = {
  evaluation: null,
  loadingEvaluation: false,
  loadingRetrieve: false,
  loadingQuery: false,
};

const apiBase = "/";
const runEvaluationBtn = document.getElementById("runEvaluationBtn");
const evaluationStatus = document.getElementById("evaluationStatus");
const metricRecall = document.getElementById("metricRecall");
const metricTotal = document.getElementById("metricTotal");
const metricPassed = document.getElementById("metricPassed");
const metricFailed = document.getElementById("metricFailed");
const metricLatency = document.getElementById("metricLatency");
const evaluationTableBody = document.getElementById("evaluationTableBody");
const customQuestionInput = document.getElementById("customQuestion");
const runRetrieveBtn = document.getElementById("runRetrieveBtn");
const runQueryBtn = document.getElementById("runQueryBtn");
const customResultsContent = document.getElementById("customResultsContent");
const exampleList = document.getElementById("exampleList");

const examples = [
  "What authentication methods does Nexus support?",
  "How does Nexus handle API rate limiting?",
  "What are the main architectural components of Nexus?",
  "How should a failed API request be troubleshooted?",
  "What are the recommended ML practices for Nexus?",
];

function setLoading(button, stateFlag, text) {
  button.disabled = stateFlag;
  if (stateFlag) {
    button.textContent = text;
  } else {
    button.textContent = button.dataset.originalText;
  }
}

function setStatus(message) {
  evaluationStatus.textContent = message;
}

function createBadge(text, isPass) {
  const span = document.createElement("span");
  span.className = `badge ${isPass ? "status-pass" : "status-fail"}`;
  span.textContent = text;
  return span;
}

function renderEvaluationTable(data) {
  evaluationTableBody.innerHTML = "";
  data.results.forEach((item) => {
    const expectedRetrieved = item.retrieved_sources.includes(item.expected_source);
    const expectedRank = expectedRetrieved ? item.retrieved_sources.indexOf(item.expected_source) + 1 : null;
    const rankLabel = expectedRank !== null ? expectedRank : "Not Found";
    const rankClass = expectedRank === 1 ? "rank-badge strong-rank" : expectedRank !== null ? "rank-badge soft-rank" : "rank-badge not-found";

    const row = document.createElement("tr");
    row.innerHTML = `
      <td><button class="example-button" type="button">${item.question}</button></td>
      <td>${item.retrieval === "PASS" ? createBadge("PASS", true).outerHTML : createBadge("FAIL", false).outerHTML}</td>
      <td>${item.expected_source}</td>
      <td>${expectedRetrieved ? createBadge("✓", true).outerHTML : createBadge("✕", false).outerHTML}</td>
      <td><span class="${rankClass}">${rankLabel}</span></td>
      <td>${item.top_source || "-"}</td>
      <td>${item.top_score.toFixed(4)}</td>
      <td>${item.latency_ms} ms</td>
    `;
    const detailButton = row.querySelector("button");
    detailButton.addEventListener("click", () => renderDetailPanel(item));
    evaluationTableBody.appendChild(row);
  });
}

function renderDetailPanel(item) {
  const expectedRetrieved = item.retrieved_sources.includes(item.expected_source);
  const expectedRank = expectedRetrieved ? item.retrieved_sources.indexOf(item.expected_source) + 1 : null;
  const rankLabel = expectedRank !== null ? expectedRank : "Not Found";
  const rankClass = expectedRank === 1 ? "rank-badge strong-rank" : expectedRank !== null ? "rank-badge soft-rank" : "rank-badge not-found";

  const chunksList = item.chunks
    .map(
      (chunk) =>
        `<div class="result-card"><h3>${chunk.document} • ${chunk.chunk_id}</h3><p><strong>Score:</strong> ${chunk.score.toFixed(4)}</p><pre>${chunk.text}</pre></div>`
    )
    .join("");

  customResultsContent.innerHTML = `
    <div class="result-card">
      <h3>Benchmark question detail</h3>
      <div class="result-row"><strong>Question</strong><span>${item.question}</span></div>
      <div class="result-row"><strong>Expected source</strong><span>${item.expected_source}</span></div>
      <div class="result-row"><strong>Expected retrieved</strong><span>${expectedRetrieved ? "Yes" : "No"}</span></div>
      <div class="result-row"><strong>Expected rank</strong><span><span class="${rankClass}">${rankLabel}</span></span></div>
      <div class="result-row"><strong>Status</strong><span>${item.retrieval}</span></div>
      <div class="result-row"><strong>Top source</strong><span>${item.top_source || "N/A"}</span></div>
      <div class="result-row"><strong>Top score</strong><span>${item.top_score.toFixed(4)}</span></div>
      <div class="result-row"><strong>Latency</strong><span>${item.latency_ms} ms</span></div>
      <div class="result-row"><strong>Answer</strong><pre>${item.answer}</pre></div>
    </div>
    ${chunksList}
  `;
}

function renderCustomResult(title, contentHtml, statusText) {
  customResultsContent.innerHTML = `
    <div class="result-card">
      <h3>${title}</h3>
      <div class="result-row"><strong>Question</strong><span>${contentHtml.question}</span></div>
      <div class="result-row"><strong>${statusText}</strong><span>${contentHtml.status}</span></div>
      <div class="result-row"><strong>Latency</strong><span>${contentHtml.latency} ms</span></div>
      <div class="result-row"><strong>Details</strong><pre>${contentHtml.details}</pre></div>
    </div>
  `;
}

function renderRetrievalOutput(item, question) {
  const chunkCards = item.chunks
    .map(
      (chunk) =>
        `<div class="result-card"><h3>${chunk.document}</h3><p><strong>Chunk ID:</strong> ${chunk.chunk_id}</p><p><strong>Score:</strong> ${chunk.score.toFixed(4)}</p><pre>${chunk.text}</pre></div>`
    )
    .join("");

  customResultsContent.innerHTML = `
    <div class="result-card">
      <h3>Retrieval-only result</h3>
      <div class="result-row"><strong>Question</strong><span>${question}</span></div>
      <div class="result-row"><strong>Latency</strong><span>${item.latency_ms} ms</span></div>
      <div class="result-row"><strong>Note</strong><span>Retrieval-only test — no OpenAI API call.</span></div>
    </div>
    ${chunkCards}
  `;
}

function renderQueryOutput(response, question) {
  const sourceCards = response.sources
    .map(
      (source) =>
        `<div class="result-card"><h3>${source.document}</h3><p><strong>Chunk ID:</strong> ${source.chunk_id}</p><p><strong>Score:</strong> ${source.score.toFixed(4)}</p></div>`
    )
    .join("");

  customResultsContent.innerHTML = `
    <div class="result-card">
      <h3>Full RAG result</h3>
      <div class="result-row"><strong>Question</strong><span>${question}</span></div>
      <div class="result-row"><strong>Latency</strong><span>${response.latency_ms} ms</span></div>
      <div class="result-row"><strong>Answer</strong><pre>${response.answer}</pre></div>
    </div>
    <div class="result-card">
      <h3>Sources</h3>
      ${sourceCards}
    </div>
  `;
}

function renderExamples() {
  exampleList.innerHTML = examples
    .map(
      (example) =>
        `<button type="button" class="example-button">${example}</button>`
    )
    .join("");

  exampleList.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => {
      customQuestionInput.value = button.textContent;
    });
  });
}

async function fetchEvaluation() {
  state.loadingEvaluation = true;
  runEvaluationBtn.disabled = true;
  setStatus("Running evaluation...");
  try {
    const response = await fetch(`${apiBase}evaluation/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });
    if (!response.ok) {
      throw new Error(`Evaluation failed: ${response.status} ${response.statusText}`);
    }
    const data = await response.json();
    state.evaluation = data;
    metricRecall.textContent = `${Math.round(data.summary.retrieval_recall * 100)}%`;
    metricTotal.textContent = data.summary.total_questions;
    metricPassed.textContent = data.summary.passed;
    metricFailed.textContent = data.summary.failed;
    metricLatency.textContent = `${data.summary.average_latency_ms} ms`;
    renderEvaluationTable(data);
    setStatus("Evaluation complete.");
  } catch (error) {
    setStatus(error.message || "Evaluation failed.");
  } finally {
    state.loadingEvaluation = false;
    runEvaluationBtn.disabled = false;
  }
}

async function runRetrieve() {
  const question = customQuestionInput.value.trim();
  if (!question) {
    setStatus("Enter a question before running retrieval.");
    return;
  }

  state.loadingRetrieve = true;
  runRetrieveBtn.disabled = true;
  runQueryBtn.disabled = true;
  setStatus("Running retrieval...");
  try {
    const response = await fetch(`${apiBase}retrieve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    if (!response.ok) {
      throw new Error(`Retrieval failed: ${response.status} ${response.statusText}`);
    }
    const data = await response.json();
    renderRetrievalOutput(data, question);
    setStatus("Retrieval complete.");
  } catch (error) {
    setStatus(error.message || "Retrieval failed.");
  } finally {
    state.loadingRetrieve = false;
    runRetrieveBtn.disabled = false;
    runQueryBtn.disabled = false;
  }
}

async function runQuery() {
  const question = customQuestionInput.value.trim();
  if (!question) {
    setStatus("Enter a question before asking AI.");
    return;
  }

  state.loadingQuery = true;
  runRetrieveBtn.disabled = true;
  runQueryBtn.disabled = true;
  setStatus("Generating answer...");
  try {
    const response = await fetch(`${apiBase}query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    if (!response.ok) {
      throw new Error(`Query failed: ${response.status} ${response.statusText}`);
    }
    const data = await response.json();
    renderQueryOutput(data, question);
    setStatus("AI generation complete.");
  } catch (error) {
    setStatus(error.message || "Query failed.");
  } finally {
    state.loadingQuery = false;
    runRetrieveBtn.disabled = false;
    runQueryBtn.disabled = false;
  }
}

runEvaluationBtn.dataset.originalText = runEvaluationBtn.textContent;
runRetrieveBtn.dataset.originalText = runRetrieveBtn.textContent;
runQueryBtn.dataset.originalText = runQueryBtn.textContent;

runEvaluationBtn.addEventListener("click", async () => {
  setLoading(runEvaluationBtn, true, "Running evaluation...");
  await fetchEvaluation();
  setLoading(runEvaluationBtn, false, runEvaluationBtn.dataset.originalText);
});

runRetrieveBtn.addEventListener("click", async () => {
  setLoading(runRetrieveBtn, true, "Running retrieval...");
  await runRetrieve();
  setLoading(runRetrieveBtn, false, runRetrieveBtn.dataset.originalText);
});

runQueryBtn.addEventListener("click", async () => {
  setLoading(runQueryBtn, true, "Generating answer...");
  await runQuery();
  setLoading(runQueryBtn, false, runQueryBtn.dataset.originalText);
});

renderExamples();
fetchEvaluation();
