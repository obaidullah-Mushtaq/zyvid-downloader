class VideoDownloader {
  constructor() {
    this.downloadCount = 0;
    this.loadingMessages = [
      "Verbindung wird hergestellt...",
      "Video wird analysiert...",
      "Qualität wird optimiert...",
      "Download wird vorbereitet...",
      "Fast fertig..."
    ];
    this.currentLoadingMessage = 0;
    this.baseUrl = "https://zyvid-downloader.onrender.com";
    
    this.initializeEventListeners();
    this.initializeAnimations();
    this.loadDownloadCount();
  }

  initializeEventListeners() {
    document.getElementById("download-form").addEventListener("submit", (e) => {
      this.handleDownload(e);
    });

    document.getElementById("url").addEventListener("input", (e) => {
      this.detectPlatform(e.target.value);
    });

    document.getElementById("url").addEventListener("focus", () => {
      this.showInputAnimation();
    });

    document.getElementById("platform").addEventListener("change", (e) => {
      this.highlightPlatformIcon(e.target.value);
    });

    document.querySelectorAll('.platform-icon').forEach(icon => {
      icon.addEventListener('click', () => {
        const platform = icon.classList[1];
        document.getElementById("platform").value = platform;
        this.highlightPlatformIcon(platform);
      });
    });

    document.getElementById("download-btn").addEventListener("mouseenter", () => {
      this.createButtonParticles();
    });
  }

  initializeAnimations() {
    this.animateCounter();
    this.observeFeatureCards();
    this.highlightPlatformIcon('youtube');
  }

  loadDownloadCount() {
    const savedCount = Math.floor(Math.random() * 50000) + 10000;
    this.downloadCount = savedCount;
    this.animateCounter();
  }

  animateCounter() {
    const counterElement = document.getElementById('downloads-counter');
    const target = this.downloadCount;
    const duration = 2000;
    const start = performance.now();

    const animate = (currentTime) => {
      const elapsed = currentTime - start;
      const progress = Math.min(elapsed / duration, 1);
      const easeOut = 1 - Math.pow(1 - progress, 3);
      const currentCount = Math.floor(easeOut * target);
      
      counterElement.textContent = this.formatNumber(currentCount);
      
      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };
    
    requestAnimationFrame(animate);
  }

  formatNumber(num) {
    return num.toLocaleString('de-DE');
  }

  detectPlatform(url) {
    const input = url.toLowerCase();
    const platformSelect = document.getElementById("platform");
    const detectedElement = document.getElementById("platform-detected");
    const detectedPlatformSpan = document.getElementById("detected-platform");
    
    let detectedPlatform = null;
    
    if (input.includes("youtube.com") || input.includes("youtu.be")) {
      detectedPlatform = "youtube";
      detectedPlatformSpan.textContent = "YouTube erkannt";
    } else if (input.includes("tiktok.com")) {
      detectedPlatform = "tiktok";
      detectedPlatformSpan.textContent = "TikTok erkannt";
    } else if (input.includes("instagram.com")) {
      detectedPlatform = "instagram";
      detectedPlatformSpan.textContent = "Instagram erkannt";
    } else if (input.includes("snapchat.com") || input.includes("t.snapchat.com")) {
      detectedPlatform = "snapchat";
      detectedPlatformSpan.textContent = "Snapchat erkannt";
    }
    
    if (detectedPlatform) {
      platformSelect.value = detectedPlatform;
      this.highlightPlatformIcon(detectedPlatform);
      detectedElement.style.display = "flex";
      detectedElement.classList.add("show");
      this.addPulseEffect(detectedElement);
    } else {
      detectedElement.classList.remove("show");
      setTimeout(() => {
        if (!detectedElement.classList.contains("show")) {
          detectedElement.style.display = "none";
        }
      }, 300);
    }
  }

  highlightPlatformIcon(platform) {
    document.querySelectorAll('.platform-icon').forEach(icon => {
      icon.classList.remove('active');
    });
    
    const activeIcon = document.querySelector(`.platform-icon.${platform}`);
    if (activeIcon) {
      activeIcon.classList.add('active');
      
      if (!document.querySelector('#dynamic-styles')) {
        const style = document.createElement('style');
        style.id = 'dynamic-styles';
        style.textContent = `
          .platform-icon.active {
            transform: scale(1.2);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
            border-color: var(--primary);
          }
        `;
        document.head.appendChild(style);
      }
    }
  }

  showInputAnimation() {
    const inputWrapper = document.querySelector('.input-wrapper');
    inputWrapper.style.transform = 'translateY(-2px)';
    inputWrapper.style.boxShadow = '0 15px 40px rgba(102, 126, 234, 0.2)';
    
    setTimeout(() => {
      inputWrapper.style.transform = '';
      inputWrapper.style.boxShadow = '';
    }, 300);
  }

  addPulseEffect(element) {
    element.style.animation = 'none';
    setTimeout(() => {
      element.style.animation = 'successPulse 0.6s ease-out';
    }, 10);
  }

  createButtonParticles() {
    const button = document.getElementById("download-btn");
    const rect = button.getBoundingClientRect();
    
    for (let i = 0; i < 3; i++) {
      const particle = document.createElement('div');
      particle.style.position = 'absolute';
      particle.style.width = '4px';
      particle.style.height = '4px';
      particle.style.background = '#fff';
      particle.style.borderRadius = '50%';
      particle.style.pointerEvents = 'none';
      particle.style.left = Math.random() * rect.width + 'px';
      particle.style.top = rect.height / 2 + 'px';
      particle.style.opacity = '0.8';
      particle.style.transition = 'all 1s ease-out';
      
      button.appendChild(particle);
      
      setTimeout(() => {
        particle.style.transform = `translateY(-20px) translateX(${(Math.random() - 0.5) * 40}px)`;
        particle.style.opacity = '0';
      }, 10);
      
      setTimeout(() => {
        if (particle.parentNode) {
          particle.remove();
        }
      }, 1000);
    }
  }

  observeFeatureCards() {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry, index) => {
        if (entry.isIntersecting) {
          setTimeout(() => {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
          }, index * 200);
        }
      });
    }, { threshold: 0.1 });

    document.querySelectorAll('.feature-card').forEach(card => {
      card.style.opacity = '0';
      card.style.transform = 'translateY(30px)';
      card.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
      observer.observe(card);
    });
  }

  async handleDownload(e) {
    e.preventDefault();
    
    const url = document.getElementById("url").value.trim();
    const platform = document.getElementById("platform").value;
    const responseEl = document.getElementById("response");
    const loadingEl = document.getElementById("loading");
    const downloadBtn = document.getElementById("download-btn");
    
    if (!url) {
      this.showError("Bitte geben Sie eine gültige URL ein.");
      return;
    }
    
    if (!this.isValidUrl(url)) {
      this.showError("Bitte geben Sie eine gültige URL ein (muss mit http:// oder https:// beginnen).");
      return;
    }
    
    responseEl.innerHTML = "";
    responseEl.className = "response-container";
    
    this.startLoading(loadingEl, downloadBtn);
    
    try {
      const response = await this.makeDownloadRequest(url, platform);
      this.stopLoading(loadingEl, downloadBtn);
      
      if (response.status === "success") {
        this.showSuccess(responseEl, response);
        this.incrementDownloadCounter();
      } else {
        this.showError(response.message || "Ein unbekannter Fehler ist aufgetreten.");
      }
    } catch (error) {
      this.stopLoading(loadingEl, downloadBtn);
      this.showError("Verbindung zum Server fehlgeschlagen. Bitte versuchen Sie es später erneut.");
      console.error("Download-Fehler:", error);
    }
  }

  isValidUrl(string) {
    try {
      new URL(string);
      return true;
    } catch (_) {
      return false;
    }
  }

  async makeDownloadRequest(url, platform) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 60000);
    
    try {
      const response = await fetch(
        `${this.baseUrl}/download?url=${encodeURIComponent(url)}&platform=${platform}`,
        { 
          signal: controller.signal,
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        }
      );
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      if (data.status === "error") {
        return data;
      }

      if (!data.download_url) {
        throw new Error("Keine gültige Download-URL empfangen.");
      }

      this.triggerDownload(data.download_url, data.filename || "video.mp4");
      return data;
    } catch (error) {
      clearTimeout(timeoutId);
      console.error("API-Fehler:", error);
      
      if (error.name === 'AbortError') {
        return {
          status: "error",
          message: "Request-Timeout: Der Server braucht zu lange für die Antwort."
        };
      }
      
      return {
        status: "error",
        message: `Download fehlgeschlagen: ${error.message}`
      };
    }
  }

  triggerDownload(url, filename) {
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.style.display = "none";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }

  startLoading(loadingEl, downloadBtn) {
    loadingEl.style.display = "block";
    loadingEl.style.opacity = "0";
    setTimeout(() => {
      loadingEl.style.opacity = "1";
    }, 10);
    
    downloadBtn.disabled = true;
    downloadBtn.style.opacity = "0.6";
    downloadBtn.style.transform = "scale(0.95)";
    
    this.currentLoadingMessage = 0;
    this.loadingMessageInterval = setInterval(() => {
      this.updateLoadingMessage();
    }, 800);
    
    loadingEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  stopLoading(loadingEl, downloadBtn) {
    loadingEl.style.opacity = "0";
    setTimeout(() => {
      loadingEl.style.display = "none";
    }, 300);
    
    downloadBtn.disabled = false;
    downloadBtn.style.opacity = "1";
    downloadBtn.style.transform = "scale(1)";
    
    if (this.loadingMessageInterval) {
      clearInterval(this.loadingMessageInterval);
    }
  }

  updateLoadingMessage() {
    const statusElement = document.getElementById("loading-status");
    if (statusElement && this.currentLoadingMessage < this.loadingMessages.length) {
      statusElement.style.opacity = "0";
      setTimeout(() => {
        statusElement.textContent = this.loadingMessages[this.currentLoadingMessage];
        statusElement.style.opacity = "1";
        this.currentLoadingMessage++;
      }, 200);
    }
  }

  showSuccess(responseEl, data) {
    responseEl.className = "response-container success show";
    responseEl.innerHTML = `
      <div class="download-success">
        <div class="success-icon">
          <i class="fas fa-check-circle"></i>
        </div>
        <h3>Download erfolgreich!</h3>
        <p><strong>${data.title}</strong> wurde erfolgreich verarbeitet.</p>
        <a href="${data.download_url}" download="${data.filename}" class="download-link">
          <i class="fas fa-download"></i>
          <span>Jetzt herunterladen</span>
        </a>
        ${data.message ? `<p style="margin-top: 1rem; font-size: 0.9rem; opacity: 0.8;">${data.message}</p>` : ''}
      </div>
    `;
    
    this.triggerCelebration();
    
    setTimeout(() => {
      responseEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 100);
  }

  showError(message) {
    const responseEl = document.getElementById("response");
    responseEl.className = "response-container error show";
    responseEl.innerHTML = `
      <div style="text-align: center;">
        <i class="fas fa-exclamation-triangle" style="font-size: 2.5rem; margin-bottom: 1rem; color: #e53e3e;"></i>
        <h3>Fehler beim Download</h3>
        <p style="margin-bottom: 1.5rem;">${message}</p>
        <button onclick="window.videoDownloader.clearForm()" style="margin: 0.5rem; padding: 0.75rem 1.5rem; background: var(--gradient-main); border: none; border-radius: 8px; color: white; cursor: pointer;">
          <i class="fas fa-redo"></i> Erneut versuchen
        </button>
      </div>
    `;
    
    responseEl.style.animation = 'shake 0.5s ease-in-out';
    setTimeout(() => {
      responseEl.style.animation = '';
    }, 500);
    
    if (!document.querySelector('#shake-styles')) {
      const style = document.createElement('style');
      style.id = 'shake-styles';
      style.textContent = `
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          25% { transform: translateX(-5px); }
          75% { transform: translateX(5px); }
        }
      `;
      document.head.appendChild(style);
    }
  }

  clearForm() {
    document.getElementById("url").value = "";
    document.getElementById("response").innerHTML = "";
    document.getElementById("response").className = "response-container";
    document.getElementById("platform-detected").style.display = "none";
  }

  triggerCelebration() {
    const colors = ['#48bb78', '#667eea', '#f093fb'];
    
    for (let i = 0; i < 20; i++) {
      const particle = document.createElement('div');
      particle.style.position = 'fixed';
      particle.style.left = Math.random() * window.innerWidth + 'px';
      particle.style.top = window.innerHeight + 'px';
      particle.style.width = Math.random() * 8 + 4 + 'px';
      particle.style.height = particle.style.width;
      particle.style.background = colors[Math.floor(Math.random() * colors.length)];
      particle.style.borderRadius = '50%';
      particle.style.pointerEvents = 'none';
      particle.style.zIndex = '9999';
      particle.style.transition = 'all 3s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
      
      document.body.appendChild(particle);
      
      setTimeout(() => {
        particle.style.transform = `translateY(-${window.innerHeight + 100}px) rotate(360deg)`;
        particle.style.opacity = '0';
      }, 100);
      
      setTimeout(() => {
        if (particle.parentNode) {
          particle.remove();
        }
      }, 3000);
    }
  }

  incrementDownloadCounter() {
    this.downloadCount++;
    this.animateCounter();
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.videoDownloader = new VideoDownloader();
  
  document.documentElement.style.scrollBehavior = 'smooth';
  
  document.querySelectorAll('button, .platform-icon, .download-link, a').forEach(el => {
    el.addEventListener('mouseenter', () => {
      document.body.style.cursor = 'pointer';
    });
    
    el.addEventListener('mouseleave', () => {
      document.body.style.cursor = 'default';
    });
  });
  
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      const form = document.getElementById('download-form');
      if (form) {
        form.dispatchEvent(new Event('submit'));
      }
    }
  });
});