#include <iostream>
#include <fstream>
#include <string>
#include <cstddef>

int main() {
    std::ifstream file;
    file.open("legenda.txt");

    if (!file.is_open()) {
        std::cerr << "Erro ao abrir legenda.txt\n";
        return 1;
    }

    // Arquivo de saída
    std::ofstream outFile;
    outFile.open("legenda_texto.txt");

    if (!outFile.is_open()) {
        std::cerr << "Erro ao criar legenda_texto.txt\n";
        return 1;
    }

    std::string line;

    while (std::getline(file, line)) {

        if (line.empty())
            continue;

        // Numero da legenda
        int index = std::stoi(line);

        // Linha do tempo
        std::string timeLine;
        std::getline(file, timeLine);

        std::size_t arrow = timeLine.find("-->");
        if (arrow == std::string::npos) continue;

        // Texto da legenda
        std::string text, textLine;
        while (std::getline(file, textLine)) {
            if (textLine.empty())
                break;

            text += textLine + " ";
        }

        // ✨ Grava somente o TEXTO no novo arquivo
        outFile << text << "\n";
    }

    file.close();
    outFile.close();

    std::cout << "Texto extraido com sucesso para texto_extraido.txt\n";
    return 0;
}