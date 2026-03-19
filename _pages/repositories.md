---
layout: page
permalink: /repositories/
title: repositories
description: Open-source repositories and contribution history across molecular ML, scientific tooling, and research engineering.
nav: true
nav_order: 4
---

<div class="page-shell">
  <p class="page-kicker">Open-source work</p>
  <p class="page-intro">A view into the repositories most relevant to my research and engineering work. The focus here is scientific tooling, chemistry AI, and the open-source systems I have contributed to most directly.</p>
</div>

{% if site.data.repositories.github_users %}

<section class="repository-section">
  <div class="section-heading">
    <h2>Profile overview</h2>
    <p>Current GitHub activity and contribution profile.</p>
  </div>

<div class="repositories d-flex flex-wrap flex-md-row flex-column justify-content-between align-items-center">
  {% for user in site.data.repositories.github_users %}
    {% include repository/repo_user.liquid username=user %}
  {% endfor %}
</div>

</section>

{% if site.repo_trophies.enabled %}
{% for user in site.data.repositories.github_users %}
{% if site.data.repositories.github_users.size > 1 %}

  <h4>{{ user }}</h4>
  {% endif %}
  <section class="repository-section">
  <div class="section-heading">
    <h2>Community footprint</h2>
    <p>Open-source participation and contribution breadth across the account.</p>
  </div>
  <div class="repositories d-flex flex-wrap flex-md-row flex-column justify-content-between align-items-center">
  {% include repository/repo_trophies.liquid username=user %}
  </div>
  </section>

{% endfor %}
{% endif %}
{% endif %}

{% if site.data.repositories.github_repos %}

<section class="repository-section">
<div class="section-heading">
  <h2>Pinned repositories</h2>
  <p>Repositories that best represent my current open-source and research engineering work.</p>
</div>

<div class="repositories d-flex flex-wrap flex-md-row flex-column justify-content-between align-items-center">
  {% for repo in site.data.repositories.github_repos %}
    {% include repository/repo.liquid repository=repo %}
  {% endfor %}
</div>
</section>
{% endif %}
