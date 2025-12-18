const fileInput = document.getElementById('fileInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const imgPreview = document.getElementById('imgPreview');
const preview = document.getElementById('preview');
const resultDiv = document.getElementById('result');
const productEl = document.getElementById('product');
const caloriesEl = document.getElementById('calories');
const sourceEl = document.getElementById('source');
const gramsInput = document.getElementById('gramsInput');

let selectedFile = null;

fileInput.addEventListener('change', (e) => {
  const f = e.target.files[0];
  if (!f) return;
  selectedFile = f;
  const url = URL.createObjectURL(f);
  imgPreview.src = url;
  imgPreview.style.display = 'block';
  preview.querySelector('.hint').style.display = 'none';
  analyzeBtn.disabled = false;
  resultDiv.style.display = 'none';
});

analyzeBtn.addEventListener('click', async () => {
  if (!selectedFile) return;
  analyzeBtn.disabled = true;
  analyzeBtn.textContent = 'Анализирую...';

  const fd = new FormData();
  fd.append('file', selectedFile);
  const grams = parseFloat(gramsInput.value) || 100;
  fd.append('grams', String(grams));

  try {
    const resp = await fetch('/analyze/', { method: 'POST', body: fd });
    if (!resp.ok) {
      const txt = await resp.text();
      throw new Error('Ошибка сервера: ' + txt);
    }
    const j = await resp.json();

    const topkHtml = j.topk.map(t => {
      const kcal = t.kcal_per_100g === null ? '—' : `${t.kcal_per_100g} ккал/100г`;
      return `<div class="topk-item"><strong>${t.label}</strong> — ${(t.probability*100).toFixed(1)}% — ${kcal}</div>`;
    }).join('');

    productEl.innerHTML = `<div style="margin-bottom:8px">Top predictions:</div>${topkHtml}`;
    caloriesEl.textContent = j.weighted_kcal_per_100g ? `≈ ${j.weighted_kcal_per_100g} ккал / 100 г` : 'Калории не найдены локально';
    sourceEl.textContent = j.estimated_total_kcal ? `Итого ≈ ${j.estimated_total_kcal} ккал для ${j.grams} г` : '';

    resultDiv.style.display = 'block';
  } catch (err) {
    productEl.textContent = 'Ошибка';
    caloriesEl.textContent = err.message;
    sourceEl.textContent = '';
    resultDiv.style.display = 'block';
  } finally {
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = 'Анализировать';
  }
});
