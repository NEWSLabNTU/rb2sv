class BidictWithNoneFilter(dict):
    """
    Similar to bidict, but allow multiple None in dictionary values,
    and all None are filtered out in its .inv_filtered dict.
    """

    @property
    def inv_filtered(self):
        # Filter out None values from the inverse dictionary view
        return {v: k for k, v in self.items() if v is not None}
