#include <iostream>
#include <fstream>
#include <string>
#include <cstddef>   // para std::size_t

int main() {
    std::ifstream file;
    file.open("legenda.txt");

    if (!file.is_open()) {
        std::cerr << "Erro ao abrir legenda.srt\n";
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
        std::string startTime = timeLine.substr(0, arrow - 1);
        std::string endTime   = timeLine.substr(arrow + 4);

        // Texto da legenda
        std::string text, textLine;
        while (std::getline(file, textLine)) {
            if (textLine.empty())
                break;

            text += textLine + " ";
        }

        //std::cout << "Legenda #" << index << "\n";
        //std::cout << "Inicio: " << startTime << "\n";
        //std::cout << "Fim: " << endTime << "\n";
        //std::cout << "Texto: " << text << "\n";
        std::cout << text << "\n";
        //std::cout << "-------------------------\n";
    }

    file.close();
    return 0;
}