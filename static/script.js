document.addEventListener('DOMContentLoaded', () => {
    // -------------------------------------------------------------
    // DOM Element Selectors
    // -------------------------------------------------------------
    const accuracyBadge = document.getElementById('accuracy-badge');
    const statTotalSamples = document.getElementById('stat-total-samples');
    const statBuyers = document.getElementById('stat-buyers');
    const statNonBuyers = document.getElementById('stat-non-buyers');
    
    const importanceContainer = document.getElementById('importance-container');
    const treeContainerDiagram = document.getElementById('tree-container-diagram');
    
    const tableBody = document.getElementById('table-body');
    const tableLimitSelect = document.getElementById('table-limit');
    const tableShowingText = document.getElementById('table-showing-text');
    
    const predictionForm = document.getElementById('prediction-form');
    const predictLoader = document.getElementById('predict-loader');
    const resultBox = document.getElementById('prediction-result-box');
    const resultAlert = document.getElementById('hasil-prediksi-alert');
    const resultStatusText = document.getElementById('result-status-text');
    const resultConfidenceText = document.getElementById('result-confidence-text');
    const recommendationList = document.getElementById('recommendation-list');

    // Helper formatting number with dot thousands separator
    const formatNumber = (num) => {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
    };

    // -------------------------------------------------------------
    // 1. Recursive Render Decision Tree Diagram
    // -------------------------------------------------------------
    const renderTreeNode = (node) => {
        const li = document.createElement('li');
        
        // Card node wrapper
        const card = document.createElement('div');
        card.className = 'tree-node-card';
        
        if (node.is_leaf) {
            const isBuy = node.name === 'Membeli';
            card.classList.add(isBuy ? 'leaf-buy' : 'leaf-nobuy');
            card.innerHTML = `
                <div class="fw-bold text-[11px] mb-1">${node.name}</div>
                <div class="text-[9px] text-muted mb-0.5">Keyakinan: <strong>${node.confidence}%</strong></div>
                <div class="text-[8px] text-muted">Sampel: ${formatNumber(node.samples)} data</div>
            `;
            li.appendChild(card);
        } else {
            card.innerHTML = `
                <div class="fw-bold text-dark">${node.name}</div>
                <div class="font-monospace text-primary fw-semibold text-[9px] mt-0.5">&le; ${node.threshold}</div>
            `;
            li.appendChild(card);
            
            // Nested branches container
            const ul = document.createElement('ul');
            
            // Left child (True branch)
            const leftLi = renderTreeNode(node.left);
            const trueLabel = document.createElement('span');
            trueLabel.className = 'branch-label true-branch';
            trueLabel.textContent = 'Benar';
            leftLi.appendChild(trueLabel);
            ul.appendChild(leftLi);
            
            // Right child (False branch)
            const rightLi = renderTreeNode(node.right);
            const falseLabel = document.createElement('span');
            falseLabel.className = 'branch-label false-branch';
            falseLabel.textContent = 'Salah';
            rightLi.appendChild(falseLabel);
            ul.appendChild(rightLi);
            
            li.appendChild(ul);
        }
        
        return li;
    };

    const buildTreeDiagram = (treeStructure) => {
        treeContainerDiagram.innerHTML = '';
        const rootUl = document.createElement('ul');
        const rootLi = renderTreeNode(treeStructure);
        rootUl.appendChild(rootLi);
        treeContainerDiagram.appendChild(rootUl);
    };

    // -------------------------------------------------------------
    // 2. Fetch Model Info and Statistics
    // -------------------------------------------------------------
    const loadModelInfo = async () => {
        try {
            const response = await fetch('/api/model-info');
            if (!response.ok) throw new Error('Gagal memuat info model');
            const data = await response.json();
            
            // Render accuracy
            accuracyBadge.textContent = `${data.accuracy}%`;
            
            // Render Stats
            statTotalSamples.textContent = formatNumber(data.total_samples);
            statBuyers.textContent = formatNumber(data.buyer_count);
            statNonBuyers.textContent = formatNumber(data.non_buyer_count);
            
            // Render Feature Importances (Bootstrap style progress bars)
            importanceContainer.innerHTML = '';
            data.feature_importances.forEach(item => {
                const barGroup = document.createElement('div');
                barGroup.className = 'mb-3';
                barGroup.innerHTML = `
                    <div class="d-flex justify-content-between text-muted mb-1" style="font-size: 0.75rem;">
                        <span>${item.feature}</span>
                        <span class="fw-bold text-dark">${item.importance}%</span>
                    </div>
                    <div class="progress" style="height: 8px;">
                        <div class="progress-bar bg-primary" role="progressbar" style="width: 0%; transition: width 0.8s;" aria-valuenow="${item.importance}" aria-valuemin="0" aria-valuemax="100"></div>
                    </div>
                `;
                importanceContainer.appendChild(barGroup);
                
                // Animate bar filling
                setTimeout(() => {
                    barGroup.querySelector('.progress-bar').style.width = `${item.importance}%`;
                }, 100);
            });
            
            // Render Visual Tree diagram
            buildTreeDiagram(data.tree_structure);
            
        } catch (error) {
            console.error('Error fetching model info:', error);
            importanceContainer.innerHTML = `<p class="text-xs text-danger"><i class="fa-solid fa-circle-exclamation"></i> Gagal memuat kontribusi fitur.</p>`;
            treeContainerDiagram.innerHTML = `<p class="text-xs text-danger"><i class="fa-solid fa-circle-exclamation"></i> Gagal merender bagan pohon.</p>`;
        }
    };

    // -------------------------------------------------------------
    // 3. Fetch and Render Dataset Table
    // -------------------------------------------------------------
    const loadDataset = async (limit = '100') => {
        tableBody.innerHTML = `
            <tr class="loading-row">
                <td colspan="9" class="p-4 text-center text-muted">
                    <div class="spinner-border spinner-border-sm text-primary me-2" role="status"></div>
                    Memuat data latih...
                </td>
            </tr>
        `;
        
        try {
            const response = await fetch(`/api/data?limit=${limit}`);
            if (!response.ok) throw new Error('Gagal mengambil data tabel');
            const data = await response.json();
            
            tableBody.innerHTML = '';
            
            if (data.data.length === 0) {
                tableBody.innerHTML = `<tr><td colspan="9" class="p-4 text-center text-muted">Tidak ada data ditemukan</td></tr>`;
                return;
            }
            
            data.data.forEach(row => {
                const tr = document.createElement('tr');
                const isBuy = row.PurchaseIntent === 'Membeli';
                const intentClass = isBuy ? 'text-success fw-bold' : 'text-danger fw-bold';
                
                tr.innerHTML = `
                    <td class="text-secondary font-monospace">#${row.ProductID}</td>
                    <td class="fw-bold text-dark">${row.ProductCategory}</td>
                    <td>${row.ProductBrand}</td>
                    <td class="fw-bold text-dark">$${row.ProductPrice}</td>
                    <td>${row.CustomerAge} Thn</td>
                    <td>${row.CustomerGender}</td>
                    <td>${row.PurchaseFrequency}x /Thn</td>
                    <td>
                        <div class="text-warning select-none">
                            ${'★'.repeat(row.CustomerSatisfaction)}${'☆'.repeat(5 - row.CustomerSatisfaction)}
                        </div>
                    </td>
                    <td class="${intentClass}">${row.PurchaseIntent}</td>
                `;
                tableBody.appendChild(tr);
            });
            
            tableShowingText.textContent = `Menampilkan ${formatNumber(data.count)} dari ${formatNumber(data.total_rows)} data`;
            
        } catch (error) {
            console.error('Error fetching table data:', error);
            tableBody.innerHTML = `
                <tr>
                    <td colspan="9" class="p-4 text-center text-danger text-xs">
                        <i class="fa-solid fa-circle-exclamation"></i> Gagal memuat data dataset. Silakan muat ulang.
                    </td>
                </tr>
            `;
        }
    };

    // Limit change event
    tableLimitSelect.addEventListener('change', (e) => {
        loadDataset(e.target.value);
    });

    // -------------------------------------------------------------
    // 4. Handle Prediction Form Submit
    // -------------------------------------------------------------
    predictionForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Hide result, show loader
        resultBox.classList.add('hidden');
        predictLoader.classList.remove('hidden');
        
        const formData = new FormData(predictionForm);
        
        const checkedSatisfaction = document.querySelector('input[name="CustomerSatisfaction"]:checked');
        const satisfactionVal = checkedSatisfaction ? checkedSatisfaction.value : '3';
        
        const checkedGender = document.querySelector('input[name="CustomerGender"]:checked');
        const genderVal = checkedGender ? checkedGender.value : '0';
        
        const payload = {
            ProductCategory: formData.get('ProductCategory'),
            ProductBrand: formData.get('ProductBrand'),
            ProductPrice: parseFloat(formData.get('ProductPrice')),
            CustomerAge: parseInt(formData.get('CustomerAge')),
            CustomerGender: parseInt(genderVal),
            PurchaseFrequency: parseInt(formData.get('PurchaseFrequency')),
            CustomerSatisfaction: parseInt(satisfactionVal)
        };
        
        // Artificial delay (600ms)
        const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));
        
        try {
            const [response] = await Promise.all([
                fetch('/api/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                }),
                delay(600)
            ]);
            
            if (!response.ok) throw new Error('Gagal menganalisis prediksi');
            const data = await response.json();
            
            // Hide loader, show results
            predictLoader.classList.add('hidden');
            resultBox.classList.remove('hidden');
            
            // Clear theme classes
            resultAlert.className = 'alert text-center shadow-sm';
            
            if (data.prediction === 1) {
                resultAlert.classList.add('alert-success');
                resultStatusText.textContent = 'NIAT BELI: TINGGI';
            } else {
                resultAlert.classList.add('alert-danger');
                resultStatusText.textContent = 'NIAT BELI: RENDAH';
            }
            
            resultConfidenceText.textContent = `${data.confidence}%`;
            
            // Render recommendations
            recommendationList.innerHTML = '';
            data.recommendations.forEach(rec => {
                const li = document.createElement('li');
                li.className = 'mb-2 leading-relaxed';
                li.innerHTML = rec;
                recommendationList.appendChild(li);
            });
            
            // Scroll down to the result
            resultBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            
        } catch (error) {
            console.error('Error submitting prediction:', error);
            predictLoader.classList.add('hidden');
            alert('Terjadi kesalahan saat memproses data prediksi. Silakan coba kembali.');
        }
    });

    // -------------------------------------------------------------
    // Initial Load
    // -------------------------------------------------------------
    loadModelInfo();
    loadDataset('100');
});
