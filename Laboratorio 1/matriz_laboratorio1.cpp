#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <chrono>
#include <cstdlib>
#include <random>

using namespace std;

const long long FILAS = 100000;
const long long COLUMNAS = 100000;
const char SEPARADOR = 2; 
const long long ANCHO_FILA = COLUMNAS + 1; 
const string PATH = "matriz_clase.bin";
const int HEADER_SIZE = 128; 

// Comprueba si el archivo ya existe en disco
bool archivo_existe(const string& path) {
    ifstream f(path.c_str());
    return f.good();
}

void marcar_como_sparse(const string& path) {
#ifdef _WIN32
    string cmd = "fsutil sparse setflag " + path;
    int result = system(cmd.c_str());
#endif
}

void crear_matriz() {
    long long total = HEADER_SIZE + (FILAS * ANCHO_FILA);

    ofstream out(PATH, ios::binary | ios::out);
    out.seekp(total - 1);
    out.write("", 1);
    out.close();

    marcar_como_sparse(PATH);

    fstream fs(PATH, ios::binary | ios::in | ios::out);
    
    string metadatos = "HEADER_MATRIZ|FILAS:" + to_string(FILAS) + 
                       "|COLUMNAS:" + to_string(COLUMNAS) + 
                       "|SEP:" + to_string(SEPARADOR);
    fs.seekp(0);
    fs.write(metadatos.c_str(), metadatos.length());

    for (long long i = 0; i < FILAS; ++i) {
        long long pos = HEADER_SIZE + ((i + 1) * ANCHO_FILA - 1);
        fs.seekp(pos);
        fs.write(&SEPARADOR, 1);
    }
    fs.close();
}

vector<char> cargar_fila_en_ram(long long num_fila) {
    ifstream in(PATH, ios::binary);
    
    long long pos = HEADER_SIZE + (num_fila * ANCHO_FILA);
    in.seekg(pos);
    
    vector<char> datos(COLUMNAS);
    in.read(datos.data(), COLUMNAS);
    in.close();
    
    return datos;
}

int main() {
    if (!archivo_existe(PATH)) {
        cout << "1. Archivo no encontrado. Creando matriz desde cero...\n";
        auto inicio = chrono::high_resolution_clock::now();
        crear_matriz();
        chrono::duration<double> dur = chrono::high_resolution_clock::now() - inicio;
        cout << "   Matriz creada en " << dur.count() << " segundos.\n\n";
    } else {
        cout << "1. El archivo ya existe. Saltando creacion.\n\n";
    }

    random_device rd;
    mt19937 gen(rd()); 
    uniform_int_distribution<long long> dist_fila(0, FILAS - 1);
    uniform_int_distribution<long long> dist_col(0, COLUMNAS - 1);

    long long fila_aleatoria = dist_fila(gen);
    long long col_aleatoria = dist_col(gen);

    cout << "2. Coordenadas aleatorias:\n";
    cout << "   -> Fila elegida: " << fila_aleatoria << "\n";
    cout << "   -> Columna elegida: " << col_aleatoria << "\n\n";

    cout << "3. Cargando SOLO la fila " << fila_aleatoria << " a la RAM...\n";
    
    vector<char> fila_en_ram = cargar_fila_en_ram(fila_aleatoria);
    
    cout << "   -> Bytes consumidos en RAM: " << fila_en_ram.size() << " bytes.\n\n";
    
    /*
    cout << "   -> Imprimiendo toda la fila extraida:\n\n";
    for (long long i = 0; i < COLUMNAS; ++i) {
        int valor_impreso = (fila_en_ram[i] == '\0') ? 0 : fila_en_ram[i];
        cout << valor_impreso; 
    }
    cout << "\n\n";
    */

    cout << "4. Buscando el valor de la columna " << col_aleatoria << "...\n";
    
    char dato_extraido = fila_en_ram[col_aleatoria];
    int valor = (dato_extraido == '\0') ? 0 : dato_extraido;

    cout << "   => RESULTADO: El dato en la coordenada (" 
         << fila_aleatoria << ", " << col_aleatoria << ") es [" << valor << "]\n";

    return 0;
}