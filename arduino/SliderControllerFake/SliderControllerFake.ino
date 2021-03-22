#include <SimpleTimer.h>           // http://arduino.cc/playground/Code/SimpleTimer
#define _DEBUG true

SimpleTimer timer;                 // Timer pour échantillonnage
const int EN =  3; 
const int PWM =  6; 
const int DIR =  9;
unsigned int tick_encodeur = 0;

int cmd = 0;                       // Commande du moteur

const int frequence_echantillonnage = 50;  // Fréquence du pid (50Hz)

/// Modifications à faire lors de la réception du moteur /////

const int rapport_reducteur = 30;          // Rapport entre le nombre de tours de l'arbre moteur et du pignon (à voir si le pignon change pas le rapport)
const int tick_par_tour_encodeur = 64;     // Nombre de tick encodeur par tour de l'arbre moteur

/// Fin modification


const float rayon_pignon = 0.026;          // Rayon du pignon (en m)

float consigne_vitesse_lineaire = 0;
float erreur_precedente = consigne_vitesse_lineaire;
float somme_erreur = 0;   // Somme des erreurs pour l'intégrateur

/// Réglage du PID

float kp = 100;           // Coefficient proportionnel
float ki = 1;           // Coefficient intégrateur
float kd = 20;           // Coefficient dérivateur

String incomingString; 
float longueur_du_banc;
float t = 0.0;

boolean start = false;


void setup() {
  // put your setup code here, to run once:
    Serial.begin(115200); 
    pinMode(EN, OUTPUT);     // Sortie moteur
    digitalWrite(EN, 1);    // Sortie moteur à 0
    pinMode(DIR, OUTPUT);     // Sortie moteur
    digitalWrite(DIR, 1);    // Sortie moteur à 0
    pinMode(PWM, OUTPUT);     // Sortie moteur
    analogWrite(PWM, 0);    // Sortie moteur à 0

    attachInterrupt(digitalPinToInterrupt(21), arret, CHANGE); //Arret par bouton manuel ou capteur effet Hall
    attachInterrupt(digitalPinToInterrupt(19), compteur, CHANGE);    // Interruption sur tick de la codeuse (interruption 0  = 19)
    attachInterrupt(digitalPinToInterrupt(18), compteur, CHANGE);    // Interruption sur tick de la codeuse (interruption 1 = 18)
    timer.setInterval(1000/frequence_echantillonnage, asservissement);  // Interruption pour calcul du PID et asservissement
}

/* Fonction principale */
void loop(){
    if (Serial.available() > 0) {
      // read the oldest byte in the serial buffer:
      incomingString = Serial.readString();

      if(incomingString[0] == 'v'){
        incomingString.remove(0,1);
        consigne_vitesse_lineaire = incomingString.toFloat();
        Serial.println(consigne_vitesse_lineaire);
        start = true;
      }

      if(incomingString[0] == 's'){
        arret();
      }
    }
    timer.run();
    delay(10);
}

void arret(){
  analogWrite(PWM, 0);    // Sortie moteur à 0
  consigne_vitesse_lineaire = 0.0;
  
}

double randomDouble(double minf, double maxf)
{
  return minf + random(1UL << 31) * (maxf - minf) / (1UL << 31);  // use 1ULL<<63 for max double values)
}

float fake_vitesse(float consigne_vitesse, int t){
  return consigne_vitesse*(1-exp(-t/10))+randomDouble(-0.01,0.01);
}


/* Interruption sur tick de la codeuse */
void compteur(){
    tick_encodeur++;  // On incrémente le nombre de tick de la codeuse
}    

void asservissement() {
    int tick = tick_encodeur;
    tick_encodeur=0;

    if(start){
      t += 1.0/frequence_echantillonnage;
    }
 
    // Calcul des erreurs
    int frequence_encodeur = frequence_echantillonnage*tick;
    //float vitesse_lineaire_reelle = rayon_pignon * (float)frequence_encodeur/(float)tick_par_tour_encodeur/(float)rapport_reducteur;
    float vitesse_lineaire_reelle = fake_vitesse(consigne_vitesse_lineaire, t);
    float erreur = consigne_vitesse_lineaire - vitesse_lineaire_reelle;
    somme_erreur += erreur;
    float delta_erreur = erreur-erreur_precedente;
    erreur_precedente = erreur;
 
    // PID : calcul de la commande
    cmd = kp*erreur + ki*somme_erreur + kd*delta_erreur;
 
    // Normalisation et contrôle du moteur
    if(cmd < 0) cmd=0;
    else if(cmd > 255) cmd = 255;
    analogWrite(PWM, cmd);
    if(_DEBUG && start)   Serial.println(vitesse_lineaire_reelle,8);
}
