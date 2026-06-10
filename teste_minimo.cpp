#include <iostream>
#include <fstream>

int main() {
    std::ifstream file;
    file.open("legenda.txt");

    if (!file.is_open()) {
        std::cout << "Nao abriu\n";
        return 0;
    }

    std::cout << "Arquivo aberto com sucesso\n";
}