<template>
  <a
    href="https://wa.link/svhddh"
    target="_blank"
    rel="noopener noreferrer"
    class="whatsapp-float"
    @click="handleClick"
    aria-label="Contactar por WhatsApp"
  >
    <svg viewBox="0 0 32 32" class="whatsapp-icon">
      <path
        fill="currentColor"
        d="M16 0C7.164 0 0 7.164 0 16c0 2.828.736 5.484 2.028 7.784L.048 31.572l8.096-2.012A15.934 15.934 0 0016 32c8.836 0 16-7.164 16-16S24.836 0 16 0zm0 29.336c-2.524 0-4.94-.7-7.008-2.012l-.504-.3-5.22 1.296 1.392-5.088-.328-.52A13.276 13.276 0 012.664 16c0-7.364 5.972-13.336 13.336-13.336S29.336 8.636 29.336 16 23.364 29.336 16 29.336zm7.304-9.98c-.4-.2-2.368-1.168-2.736-1.3-.368-.132-.636-.2-.904.2-.268.4-1.036 1.3-1.272 1.568-.236.268-.472.3-.872.1-.4-.2-1.688-.624-3.216-1.988-1.188-1.06-1.988-2.368-2.22-2.768-.232-.4-.024-.616.176-.816.18-.18.4-.472.6-.708.2-.236.268-.4.4-.668.132-.268.068-.5-.032-.7-.1-.2-.904-2.176-1.24-2.98-.328-.784-.66-.676-.904-.688-.232-.012-.5-.016-.768-.016s-.704.1-1.072.5c-.368.4-1.404 1.372-1.404 3.344s1.436 3.88 1.636 4.148c.2.268 2.828 4.32 6.852 6.056.956.412 1.704.66 2.288.844.96.304 1.836.26 2.528.156.772-.116 2.368-.968 2.7-1.904.332-.936.332-1.74.232-1.904-.1-.164-.368-.264-.768-.464z"
      />
    </svg>
  </a>
</template>


<script>
import { trackWhatsAppClick } from '@/utils/tracking.js'

export default {
  name: 'WhatsAppButton',
  methods: {
    handleClick() {
      trackWhatsAppClick('whatsapp-float-button', 'floating-widget')
    }
  }
}
</script>

<style scoped>
.whatsapp-float {
  position: fixed;
  bottom: 30px;
  right: 30px;
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #25D366, #128C7E);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(37, 211, 102, 0.4);
  z-index: 999;
  transition: all 0.3s ease;
  animation: pulse-whatsapp 2s infinite;
  cursor: pointer;
  text-decoration: none;
}

.whatsapp-float:hover {
  transform: scale(1.1) translateY(-3px);
  box-shadow: 0 12px 32px rgba(37, 211, 102, 0.6);
}

.whatsapp-icon {
  width: 32px;
  height: 32px;
  color: white;
}

@keyframes pulse-whatsapp {
  0%, 100% {
    box-shadow: 0 8px 24px rgba(37, 211, 102, 0.4);
  }
  50% {
    box-shadow: 0 8px 24px rgba(37, 211, 102, 0.7);
  }
}

@media (max-width: 768px) {
  .whatsapp-float {
    width: 56px;
    height: 56px;
    bottom: 20px;
    right: 20px;
  }

  .whatsapp-icon {
    width: 28px;
    height: 28px;
  }
}
</style>
