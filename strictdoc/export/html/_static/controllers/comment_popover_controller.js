(() => {
  class CommentPopover extends Stimulus.Controller {
    close(event) {
      // Prevent form submissions or link navigation
      event.preventDefault(); 
      
      console.log("close", event)

      this.element.classList.add('hidden');
    }
  }

  class CommentAutoscroll extends Stimulus.Controller {
    connect() {
      // scrollHeight is the total height of the content
      this.element.scrollTop = this.element.scrollHeight;
    }
  }

  Stimulus.application.register("comment-popover", CommentPopover);
  Stimulus.application.register("comment-autoscroll", CommentAutoscroll);

})();