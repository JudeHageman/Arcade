class SparseMatrixBase:
    """Interface definition. Your SparseMatrix must inherit from this."""

    def __init__(self, rows=None, cols=None, default=0):
        self.rows    = rows
        self.cols    = cols
        self.default = default

    def set(self, row, col, value):
        raise NotImplementedError

    def get(self, row, col):
        raise NotImplementedError

    def items(self):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def multiply(self, other):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError


# =============================================================================
# Your implementation goes here.
# =============================================================================

from .array import ArrayList

class SparseMatrix(SparseMatrixBase):
    """Sparse matrix implementation using COO."""

    def __init__(self, rows=None, cols=None, default=0):
        super().__init__(rows, cols, default)

        self.data = ArrayList()

    def set(self, row, col, value):
        for i in range(len(self.data)):
            item = self.data[i]
            item_row = item[0]
            item_col = item[1]
            
            if item_row == row and item_col == col:
                self.data.pop(i)
                break
        
        if value != self.default:
            self.data.append((row, col, value))

    def get(self, row, col):
        for i in range(len(self.data)):
            item = self.data[i]
            item_row = item[0]
            item_col = item[1]
            item_value = item[2]
            
            if item_row == row and item_col == col:
                return item_value
        
        return self.default

    def items(self):
        result = ArrayList()

        for i in range(len(self.data)):
            item = self.data[i]
            key = (item[0], item[1])
            val = item[2]
            result.append((key, val))

        return result

    def __len__(self):
        return len(self.data)

    def multiply(self, other):
        result = SparseMatrix(self.rows, other.cols, self.default)

        for i in range(self.rows):
            for j in range(other.cols):
                sum_value = 0
                for k in range(self.cols):
                    value_1 = self.get(i, k)
                    value_2 = other.get(k, j)
                    product = value_1 * value_2
                    sum_value = sum_value + product
                
                if sum_value != result.default:
                    result.set(i, j, sum_value)
        
        return result

    def __str__(self):
        output = ""

        for i in range(self.rows):
            for j in range(self.cols):
                value = self.get(i, j)
                output = output + str(value) + " "
            output = output + "\n"
            
        return output
