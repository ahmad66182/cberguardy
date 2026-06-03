// Page Navigation
function showPage(id) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  const target = document.getElementById('page-' + id);
  if (target) target.classList.add('active');
  window.scrollTo({ top: 0, behavior: 'smooth' });
  setTimeout(initReveal, 100);
}

// Mobile Menu Toggle
function toggleMenu() {
  document.getElementById('mobileMenu').classList.toggle('open');
}

// Initialize Reveal Animations
function initReveal() {
  const items = document.querySelectorAll('.reveal:not(.vis)');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((e, i) => {
      if (e.isIntersecting) {
        setTimeout(() => e.target.classList.add('vis'), i * 80);
        observer.unobserve(e.target);
      }
    });
  }, { threshold: 0.1 });
  items.forEach(el => observer.observe(el));
}

// Navbar Scroll Effect
window.addEventListener('scroll', () => {
  const nav = document.getElementById('nav');
  if (nav) nav.style.background = window.scrollY > 40 ? 'rgba(10,12,18,0.95)' : 'rgba(10,12,18,0.85)';
});

// FAQ Toggle Function
function toggleFaq(element) {
  element.classList.toggle('active');
}

// ============ CONTACT FORM WITH AJAX ============
const WEBSITE_API_URL = '';

function validateName(input) {
  input.value = input.value.replace(/[^a-zA-Z\s]/g, '');
}

function validatePhone(input) {
  input.value = input.value.replace(/[^0-9+\s-]/g, '');
}

function validateEmail(input) {
  if (input.value.length > 0 && !input.value.includes('@')) {
    input.style.borderColor = '#ef4444';
  } else {
    input.style.borderColor = '';
  }
}

async function submitContactForm() {
  const name = document.getElementById('fname').value.trim();
  const phone = document.getElementById('fphone').value.trim();
  const email = document.getElementById('femail').value.trim();
  const reasonSelect = document.getElementById('freason');
  const reason = reasonSelect.value;
  const message = document.getElementById('fmsg').value.trim();

  // Validation
  if (!name) {
    alert("Please enter your full name.");
    return;
  }
  if (!phone) {
    alert("Please enter your phone number.");
    return;
  }
  if (!email || !email.includes('@')) {
    alert("Please enter a valid email address.");
    return;
  }
  if (!reason) {
    alert("Please select a reason.");
    return;
  }

  // Prepare data
  const formData = {
    name: name,
    phone: phone,
    email: email,
    reason: reason,
    message: message
  };

  // Show loading state
  const submitBtn = document.querySelector('#formContent .btn-primary');
  const originalText = submitBtn.innerHTML;
  submitBtn.innerHTML = '⏳ Sending...';
  submitBtn.disabled = true;

  try {
    const response = await fetch(`${WEBSITE_API_URL}/api/contact`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData)
    });

    const result = await response.json();

    if (response.ok && result.success) {
      // Show success
      document.getElementById('formContent').style.display = 'none';
      document.getElementById('formSuccess').style.display = 'block';
      document.getElementById('formError').style.display = 'none';
    } else {
      throw new Error(result.error || 'Submission failed');
    }
  } catch (error) {
    console.error('Error:', error);
    // Show error
    document.getElementById('formContent').style.display = 'none';
    document.getElementById('formError').style.display = 'block';
  } finally {
    // Reset button
    submitBtn.innerHTML = originalText;
    submitBtn.disabled = false;
  }
}

function resetContactForm() {
  document.getElementById('formContent').style.display = 'block';
  document.getElementById('formSuccess').style.display = 'none';
  document.getElementById('formError').style.display = 'none';
  
  ['fname', 'fphone', 'femail', 'fmsg'].forEach(id => { 
    const el = document.getElementById(id); 
    if (el) el.value = ''; 
  });
  
  const reason = document.getElementById('freason');
  if (reason) reason.selectedIndex = 0;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  initReveal();
  
  // Close mobile menu when clicking outside
  document.addEventListener('click', (e) => {
    const mobileMenu = document.getElementById('mobileMenu');
    const hamburger = document.querySelector('.hamburger');
    
    if (mobileMenu && mobileMenu.classList.contains('open')) {
      if (!mobileMenu.contains(e.target) && !hamburger?.contains(e.target)) {
        mobileMenu.classList.remove('open');
      }
    }
  });
});
