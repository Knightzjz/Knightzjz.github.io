---
layout: default
title: "Ji-Zhe (Knight) Zhou"
---

<div class="home-container">
  <!-- Hero Section -->
  <header class="hero">
    <div class="avatar-wrapper">
      <img src="{{ site.avatar }}" alt="{{ site.author }}" class="avatar">
    </div>
    <div class="hero-text">
      <h1>Ji-Zhe Zhou （周吉喆）</h1>
      <p class="position-cn">四川大学计算机学院副教授</p>
      <div class="position-divider"></div>
      <p class="position-en">Associate Professor at Sichuan University</p>
      
      <div class="links">
        <a href="https://github.com/{{ site.github_username }}" target="_blank" class="btn">
          <svg height="16" width="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
          GitHub
        </a>
        <a href="https://scholar.google.com/citations?user=-cNWmJMAAAAJ" target="_blank" class="btn scholar">
          <svg height="16" width="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 3L1 9l4 2.18v6L12 21l7-3.82v-6l2-1.09V17h2V9L12 3zm6.82 6L12 12.72 5.18 9 12 5.28 18.82 9zM17 15.99l-5 2.73-5-2.73v-3.72L12 15l5-2.73v3.72z"/></svg>
          Scholar <span id="citation-count"></span>
        </a>
        <a href="{{ '/blog/' | relative_url }}" class="btn blog">
          <svg height="16" width="16" viewBox="0 0 24 24" fill="currentColor"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg>
          Blog
        </a>
      </div>
    </div>
  </header>

  <script>
    fetch('/data/citations.json')
      .then(response => response.json())
      .then(data => {
        document.getElementById('citation-count').textContent = '(' + data.citations + ')';
      })
      .catch(error => console.log('Citation data not available'));
  </script>

  <!-- Bio Section -->
  <section class="bio-section">
    <p class="bio-text">
      <!-- 请在此处填入您的个人简介 -->
      [您的个人简介内容将在这里展示，请告诉我具体文字，我来替换这里的占位符。]
    </p>
  </section>

  <!-- Publications -->
  <section class="section">
    <h2>📚 Selected Publications</h2>
    <div class="pub-list">
      <article class="pub">
        <span class="badge spotlight">🎯 NeurIPS 2024 Spotlight</span>
        <h3>IMDL-BenCo: A Comprehensive Benchmark for Image Manipulation Detection & Localization</h3>
        <p class="authors"><strong>J Zhou</strong>, Z Chen, W Wang, Z Xia</p>
      </article>
      <article class="pub">
        <span class="badge oral">⭐ ICCV 2023 Oral (Top 5%)</span>
        <h3>Pre-training-free Image Manipulation Localization via Non-Mutually Contrastive Learning</h3>
        <p class="authors"><strong>J Zhou</strong>, Z Chen, W Wang</p>
      </article>
      <article class="pub">
        <span class="badge">NeurIPS 2025</span>
        <h3>ForensicHub: Towards Universal Fake Image Detection and Localization</h3>
        <p class="authors"><strong>J Zhou</strong>, et al.</p>
      </article>
    </div>
  </section>

  <!-- Experience -->
  <section class="section">
    <h2>💼 Experience</h2>
    <div class="timeline">
      <div class="item">
        <span class="date">2022 – Present</span>
        <div class="content">
          <h3>Associate Professor</h3>
          <p>Sichuan University, College of Computer Science</p>
          <span class="tag highlight">四川省千人计划入选者</span>
        </div>
      </div>
      <div class="item">
        <span class="date">Education</span>
        <div class="content">
          <h3>B.S., M.S., Ph.D.</h3>
          <p>University of Macau</p>
        </div>
      </div>
    </div>
  </section>

  <!-- Services -->
  <section class="section">
    <h2>🏛️ Professional Services</h2>
    <ul class="services">
      <li><strong>Associate Editor:</strong> IEEE TETCI</li>
      <li><strong>Area Chair:</strong> PRCV 2025, ChinaMFS</li>
      <li><strong>Senior PC:</strong> NeurIPS, ACM MM, ICCV</li>
    </ul>
  </section>
</div>
