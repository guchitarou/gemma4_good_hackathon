// assets/tooltip.js

function initTooltip() {
    const cy = window.cy;
    if (!cy) {
        setTimeout(initTooltip, 300);  // cyが準備できるまでリトライ
        return;
    }

    const tooltip = document.getElementById('tooltip');
    if (!tooltip) {
        console.log("[initTooltip] tooltip要素が見つからない。300ms後にリトライ...");
        setTimeout(initTooltip, 300);
        return;
    }

    // マウス移動でツールチップ追従
    document.addEventListener('mousemove', function(e) {
        tooltip.style.left = (e.clientX + 14) + 'px';
        tooltip.style.top  = (e.clientY + 14) + 'px';
    });

    // エッジに乗ったら表示
    cy.on('mouseover', 'edge', function(e) {
        const edge = e.target;
        const src  = edge.data('source');
        const tgt  = edge.data('target');
        const rel = edge.data('label') || '関係なし';
        tooltip.innerText = `${rel}`;
        tooltip.style.display = 'block';
    });

    // エッジから離れたら非表示
    cy.on('mouseout', 'edge', function (e) {
        tooltip.style.display = 'none';
    });
}

// DOM構築後に実行
document.addEventListener('DOMContentLoaded', function () {
    initTooltip();
});