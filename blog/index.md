---
layout: default
title: "Blog"
permalink: /blog/
---

<div class="blog-header">
  <h1>📝 Blog</h1>
  <p>Thoughts on AI, research, and technology</p>
</div>

<div class="blog-list">
  {% for post in site.posts %}
  <a href="{{ post.url }}" class="blog-item">
    <h2>{{ post.title }}</h2>
    <p class="meta">{{ post.date | date: "%B %d, %Y" }}</p>
    <p>{{ post.description | default: post.content | truncate: 150 }}</p>
  </a>
  {% endfor %}
</div>
