from PyQt5 import QtGui

class ColorUtils:

    @staticmethod
    def blend_colors(color1: QtGui.QColor, color2: QtGui.QColor) -> QtGui.QColor:
        """Blend two QColor objects using the weight of their alpha values.

        Args:
            color1 (QtGui.QColor): The first color.
            color2 (QtGui.QColor): The second color.

        Returns:
            QtGui.QColor: The resulting blended color.
        """
        r1, g1, b1, a1 = color1.getRgb()
        r2, g2, b2, a2 = color2.getRgb()

        # Return transparent color if total alpha is zero
        total_alpha = a1 + a2
        if total_alpha == 0:
            return QtGui.QColor(0, 0, 0, 0)

        # Blend the RGB components using the alpha weights
        r = min((r1 * a1 + r2 * a2) // total_alpha, 255)
        g = min((g1 * a1 + g2 * a2) // total_alpha, 255)
        b = min((b1 * a1 + b2 * a2) // total_alpha, 255)

        # The alpha of the resulting color is the sum of the alphas (clamped to 255)
        a = min(total_alpha, 255)

        return QtGui.QColor(r, g, b, a)
