/**
 * PrivateEye Overlay Geometry Engine
 *
 * Implements mathematically exact coordinate mapping from source image space
 * to display space within CSS `object-fit: contain` letterboxed viewports.
 *
 * Prevents bounding box drift across arbitrary aspect ratios, container sizes,
 * and display scaling / DPR changes.
 */

(function (root, factory) {
  if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.PrivateEyeGeometry = factory();
  }
})(typeof self !== 'undefined' ? self : this, function () {
  /**
   * Computes display geometry for an image contained within a container.
   *
   * @param {number} containerWidth - Outer viewport width in pixels
   * @param {number} containerHeight - Outer viewport height in pixels
   * @param {number} sourceWidth - Native source image width in pixels
   * @param {number} sourceHeight - Native source image height in pixels
   * @returns {Object} { scale, displayWidth, displayHeight, offsetX, offsetY }
   */
  function calculateContainment(containerWidth, containerHeight, sourceWidth, sourceHeight) {
    if (!containerWidth || !containerHeight || !sourceWidth || !sourceHeight) {
      return {
        scale: 1,
        displayWidth: containerWidth || 0,
        displayHeight: containerHeight || 0,
        offsetX: 0,
        offsetY: 0,
      };
    }

    const scale = Math.min(
      containerWidth / sourceWidth,
      containerHeight / sourceHeight
    );

    const displayWidth = sourceWidth * scale;
    const displayHeight = sourceHeight * scale;

    const offsetX = (containerWidth - displayWidth) / 2;
    const offsetY = (containerHeight - displayHeight) / 2;

    return {
      scale,
      displayWidth,
      displayHeight,
      offsetX,
      offsetY,
    };
  }

  /**
   * Transforms a bounding box from native source coordinates to display coordinates.
   *
   * @param {Object} box - { x, y, width, height } in source pixel coordinates
   * @param {Object} geom - Geometry object returned by calculateContainment
   * @returns {Object} { left, top, width, height } in pixels relative to the container
   */
  function transformBoundingBox(box, geom) {
    if (!box || !geom) {
      return { left: 0, top: 0, width: 0, height: 0 };
    }

    return {
      left: box.x * geom.scale + geom.offsetX,
      top: box.y * geom.scale + geom.offsetY,
      width: box.width * geom.scale,
      height: box.height * geom.scale,
    };
  }

  return {
    calculateContainment,
    transformBoundingBox,
  };
});
