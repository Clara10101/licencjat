# licencjat

Celem pracy było stworzenie narzędzia umożliwiającego przeprowadzenie symulacji ekspresji genów jedną z dotychczasowych implementacji algorytmu STOPS w oparciu o podane parametry. Powstałe narzędzie nazywane dalej stops_web jest modułem języka Python, który został zintegrowany z serwisem WeBIAS co umożliwiło zdalne wykonywanie symulacji stochastycznych sieci logicznych przy pomocy różnych implementacji modelu STOPS. 

Aby wykonać symulację należy uzupełnić obecny na stronie formularz podając w sekcji Input data plik zawierający parametry symulacji (plik zapisany w formacie JSON zgodny z opisem z punktu 2.3 pracy) oraz wybierając rodzaje symulacji, które zostaną wykonane w oparciu o dane pochodzące z przesłanego pliku. Wyboru rodzajów symulacji można dokonać poprzez zaznaczenie odpowiednich pól wyboru typu checkbox, gdzie Population of cells, Hexagonal grid oraz Segments odnosza się odpowiednio do symulacji populacji komórek w czasie, komunikacji pomiędzy komórkami w przestrzeni oraz procesu segmentacji u Drosophila melanogaster.

Pliki JSON umożliwiające wykonanie trzech (opisanych w pracy) przykładowych symulacji można znaleźć poniżej. 

Po wykonaniu symulacji jej wyniki są dostępne dla użytownika w postaci możliwych do pobrania plików w formatach pdf oraz pickle. W przypadku plików z rozszerzeniem pickle serwis WeBIAS tworzy również link do aplikacji umożliwiającej wizualizację wyników na serwerze, w postaci statycznych wykesów lub animacji.

Przykładowe pliki JSON do wykonania trzech rodzajów symulacji:
* symulacja populacji komórek w czasie - przykladstops1.json
* symulacja komunikacji pomiędzy komórkami w przestrzeni - przykladstops2.json
* symulacja procesu segmentacji podczas rozwoju Drosophila melanogaster - przykladstops3.json
