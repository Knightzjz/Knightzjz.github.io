---
layout: default
title: "Ji-Zhe (Knight) Zhou"
---

<div class="home-container">
  <!-- Hero Section -->
  <header class="hero">
    <img src="{{ site.avatar }}" alt="{{ site.author }}" class="avatar">
    <div class="hero-text">
      <h1>{{ site.title }}</h1>
      <p class="position">{{ site.position }} · {{ site.affiliation }}</p>
      <p class="bio">{{ site.description }}</p>
      
      <div class="interests">
        {% for interest in site.research_interests %}
        <span class="tag">{{ interest }}</span>
        {% endfor %}
      </div>
      
      <div class="links">
        <a href="https://github.com/{{ site.github_username }}" target="_blank" class="btn">
          <svg height="16" width="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
          GitHub
        </a>
        <a href="{{ '/blog/' | relative_url }}" class="btn secondary">
          📝 Read Blog
        </a>
      </div>
    </div>
  </header>

  <!-- Stats -->
  <section class="stats">
    <div class="stat"><span class="num">30+</span><span class="label">Papers</span></div>
    <div class="stat"><span class="num">800+</span><span class="label">Citations</span></div>
    <div class="stat"><span class="num">7k+</span><span class="label">GitHub Stars</span></div>
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
