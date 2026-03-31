(() => {
  class InlineComment extends Stimulus.Controller {
    async open(event) {
      event.preventDefault();
      event.stopPropagation();

      console.log("open", event)

      const threadId = this.element.dataset.threadId;
      
      // Find the specific sdoc-node we are currently inside
      const parentNode = this.element.closest('sdoc-node');
      if (!parentNode) return;

      
      // Find the popover hidden inside this specific sdoc-node
      let targetPopover = parentNode.querySelector(`.sdoc-thread-popover[data-thread-id="${threadId}"]`);
            
      if (!targetPopover) {        
        try {
          const fetchUrl = this.element.href; 
          const response = await fetch(fetchUrl);
          
          if (!response.ok) throw new Error("Failed to load comment form");
          
          const htmlSnippet = await response.text();
          
          parentNode.insertAdjacentHTML('beforeend', htmlSnippet);
          targetPopover = parentNode.querySelector(`.sdoc-thread-popover[data-thread-id="${threadId}"]`);
        } catch (error) {
          console.error("Error loading discussion:", error);
          return; 
        }
      }

      // We hide any other open popovers first
      document.querySelectorAll('.sdoc-thread-popover').forEach(p => {
        p.classList.add('hidden');
      });

      // Calculate left position
      const spanRect = this.element.getBoundingClientRect();
      const nodeRect = parentNode.getBoundingClientRect();   
      const finalLeftPos = nodeRect.right + 40;

      // Temporarly position at topto measure height
      targetPopover.style.visibility = 'hidden';
      targetPopover.style.left = `${finalLeftPos}px`;
      targetPopover.style.top = '0px';
      targetPopover.classList.remove('hidden');

        
      const popoverHeight = targetPopover.offsetHeight;
      const viewportHeight = window.innerHeight;
      const safeMargin = 32;

      // Start with the ideal position (aligned with the text)
      let topPos = spanRect.top;

      // Bottom Collision Check?
      if (topPos + popoverHeight > viewportHeight - safeMargin) {
        // Push it up so the bottom of the popover rests safely inside the viewport
        topPos = viewportHeight - popoverHeight - safeMargin;
      }

      // Top Collision Check?
      if (topPos < safeMargin) {
        topPos = safeMargin;
      }

      // Apply the calculated coordinates and reveal
      targetPopover.style.top = `${topPos}px`;
      targetPopover.style.visibility = '';

      // scroll the messages to the bottom to see newest
      const messagesBox = targetPopover.querySelector('.sdoc-thread-messages');
      if (messagesBox) {
        messagesBox.scrollTop = messagesBox.scrollHeight;
      }

      // Hide again if the user scrolls the page
      const scrollHandler = (e) => {
        if (targetPopover.contains(e.target)) {
          return;
        }
        targetPopover.classList.add('hidden');
        window.removeEventListener('scroll', scrollHandler, true);
      };
      window.addEventListener('scroll', scrollHandler, true);
    }
  }

  Stimulus.application.register("inline-comment", InlineComment);

})();