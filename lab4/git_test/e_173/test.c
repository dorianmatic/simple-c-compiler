int main(void) {
    int x = 10;
    {
        int y = x - 2;
        {
            int z = y + 19;
            return x;
        }
    }
    return 0;
}