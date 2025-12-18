document.addEventListener('DOMContentLoaded', () => {
  const fileInput = document.getElementById('fileInput');
  const analyzeBtn = document.getElementById('analyzeBtn');
  const clearBtn = document.getElementById('clearBtn');
  const imgPreview = document.getElementById('imgPreview');
  const preview = document.getElementById('preview');
  const resultDiv = document.getElementById('result');
  const predictionsEl = document.getElementById('predictions');
  const caloriesEl = document.getElementById('calories');
  const sourceEl = document.getElementById('source');
  const gramsInput = document.getElementById('gramsInput');
  
  let selectedFile = null;
  let model = null;
  
  async function loadModel() {
    try {
      console.log('🔄 Загрузка модели MobileNet...');
      model = await mobilenet.load({
        version: 2,
        alpha: 1.0
      });
      console.log('✅ Модель загружена');
    } catch (error) {
      console.error('❌ Ошибка загрузки модели:', error);
      showError('Не удалось загрузить модель анализа изображений');
    }
  }
  
  loadModel();
  
  fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    selectedFile = file;
    
    if (!file.type.startsWith('image/')) {
      showError('Пожалуйста, выберите файл изображения');
      return;
    }
    
    const reader = new FileReader();
    reader.onload = (e) => {
      imgPreview.src = e.target.result;
      imgPreview.style.display = 'block';
      preview.querySelector('.hint').style.display = 'none';
      analyzeBtn.disabled = false;
      resultDiv.style.display = 'none';
    };
    reader.readAsDataURL(file);
  });
  
  clearBtn.addEventListener('click', () => {
    fileInput.value = '';
    selectedFile = null;
    imgPreview.src = 'placeholder.jpg';
    imgPreview.style.display = 'none';
    preview.querySelector('.hint').style.display = 'block';
    analyzeBtn.disabled = true;
    resultDiv.style.display = 'none';
    predictionsEl.innerHTML = '';
    caloriesEl.textContent = '';
    sourceEl.textContent = '';
  });
  
  analyzeBtn.addEventListener('click', async () => {
    if (!selectedFile || !model) return;
    
    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = '<span class="loading"></span> Анализ...';
    resultDiv.style.display = 'none';
    
    try {
      const image = new Image();
      image.src = URL.createObjectURL(selectedFile);
      
      await new Promise((resolve) => {
        image.onload = resolve;
      });
      
      const predictions = await model.classify(image, 5);
      
      let weightedCalories = 0;
      let weightSum = 0;
      const grams = parseFloat(gramsInput.value) || 100;
      
      const predictionsHTML = predictions.map(pred => {
        const calories = findCalorieMatch(pred.className);
        const probability = (pred.probability * 100).toFixed(1);
        
        let calorieText = 'не найдены';
        if (calories !== null) {
          calorieText = `${calories} ккал/100г`;
          weightedCalories += pred.probability * calories;
          weightSum += pred.probability;
        }
        
        return `
          <div class="prediction-item">
            <strong>${pred.className}</strong><br>
            <span class="probability">Вероятность: ${probability}%</span><br>
            <span class="calories">Калории: ${calorieText}</span>
          </div>
        `;
      }).join('');
      
      predictionsEl.innerHTML = predictionsHTML;
      
      if (weightSum > 0) {
        const avgCaloriesPer100g = weightedCalories / weightSum;
        const totalCalories = (avgCaloriesPer100g / 100) * grams;
        
        caloriesEl.textContent = `Среднее: ${avgCaloriesPer100g.toFixed(1)} ккал на 100 г`;
        sourceEl.textContent = `Итого для ${grams} г: ${totalCalories.toFixed(0)} ккал`;
      } else {
        caloriesEl.textContent = 'Калории не найдены в базе данных';
        sourceEl.textContent = 'Расширьте базу данных в calorie-database.js';
      }
      
      resultDiv.style.display = 'block';
      
    } catch (error) {
      console.error('Ошибка анализа:', error);
      showError(`Ошибка анализа изображения: ${error.message}`);
    } finally {
      analyzeBtn.disabled = false;
      analyzeBtn.textContent = '🔍 Анализировать';
    }
  });
  
  function showError(message) {
    predictionsEl.innerHTML = `<div style="color: #f87171;">${message}</div>`;
    caloriesEl.textContent = '';
    sourceEl.textContent = '';
    resultDiv.style.display = 'block';
  }
  
  gramsInput.addEventListener('change', () => {
    if (resultDiv.style.display !== 'none') {
      analyzeBtn.click();
    }
  });
});